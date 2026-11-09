//! 「今日窝囊费」：打工人实时摸鱼回血与发薪日倒计时模块。

use crate::app::{App, Env};
use crate::model::{config_dir, Settings};
use crate::paint::{Card, H};
use crate::theme::{self, W};
use chrono::{Datelike, Local, NaiveDate, Timelike};
use eframe::egui::{self, Color32, Pos2, Rect, RichText, Vec2};
use std::fs;
use std::sync::{Mutex, OnceLock};

const GOLD: Color32 = Color32::from_rgb(255, 204, 72);
const GOLD_DIM: Color32 = Color32::from_rgb(68, 54, 22);

const QUOTES: &[&str] = &[
    "忍一时越想越气，看一眼窝囊费再忍五分钟",
    "老板画的饼消化不良，只有到账的窝囊费最踏实",
    "只要我摸鱼够快，资本家就薅不到我的羊毛",
    "带薪喝水 +1，带薪发呆 +1，今日回血稳步推进",
    "工作是老板的，窝囊费和身体是自己的",
    "别生气，你现在皱的每一道眉头都是明码标价的",
    "今日已含泪怒赚一杯奶茶钱，稳住别浪",
    "虽然班上得很窝囊，但钱跳动的样子真的很迷人",
];

#[derive(Clone, Debug, PartialEq)]
pub struct WonangConfig {
    pub monthly_salary: f64,
    /// 0 = 双休(21.75天), 1 = 大小周(24天), 2 = 单休(26天), 3 = 全勤(30天)
    pub rest_mode: u8,
    pub start_hour: u32,
    pub start_min: u32,
    pub end_hour: u32,
    pub end_min: u32,
    pub payday: u32,
    /// 0 = 仅展开页显示, 1 = 收起时与时间轮播, 2 = 收起时常驻显示
    pub pill_mode: u8,
    pub quote_offset: usize,
}

impl Default for WonangConfig {
    fn default() -> Self {
        Self {
            monthly_salary: 10000.0,
            rest_mode: 0,
            start_hour: 9,
            start_min: 0,
            end_hour: 18,
            end_min: 0,
            payday: 15,
            pill_mode: 0,
            quote_offset: 0,
        }
    }
}

impl WonangConfig {
    pub fn work_days_per_month(&self) -> f64 {
        match self.rest_mode {
            0 => 21.75,
            1 => 24.0,
            2 => 26.0,
            _ => 30.0,
        }
    }

    pub fn rest_label(&self) -> &'static str {
        match self.rest_mode {
            0 => "双休",
            1 => "大小周",
            2 => "单休",
            _ => "全勤",
        }
    }

    fn load_from_disk() -> Self {
        let mut cfg = Self::default();
        let path = config_dir().join("wonangfei.txt");
        if let Ok(text) = fs::read_to_string(path) {
            for line in text.lines() {
                if let Some((k, v)) = line.split_once('=') {
                    let (k, v) = (k.trim(), v.trim());
                    match k {
                        "monthly_salary" => cfg.monthly_salary = v.parse::<f64>().unwrap_or(10000.0).clamp(100.0, 10_000_000.0),
                        "rest_mode" => cfg.rest_mode = v.parse::<u8>().unwrap_or(0).min(3),
                        "start_hour" => cfg.start_hour = v.parse::<u32>().unwrap_or(9).min(23),
                        "start_min" => cfg.start_min = v.parse::<u32>().unwrap_or(0).min(59),
                        "end_hour" => cfg.end_hour = v.parse::<u32>().unwrap_or(18).min(23),
                        "end_min" => cfg.end_min = v.parse::<u32>().unwrap_or(0).min(59),
                        "payday" => cfg.payday = v.parse::<u32>().unwrap_or(15).clamp(1, 31),
                        "pill_mode" => cfg.pill_mode = v.parse::<u8>().unwrap_or(0).min(2),
                        "quote_offset" => cfg.quote_offset = v.parse::<usize>().unwrap_or(0),
                        _ => {}
                    }
                }
            }
        }
        cfg
    }

    pub fn save_to_disk(&self) {
        let path = config_dir().join("wonangfei.txt");
        if let Some(parent) = path.parent() {
            let _ = fs::create_dir_all(parent);
        }
        let body = format!(
            "monthly_salary={:.2}\nrest_mode={}\nstart_hour={}\nstart_min={}\nend_hour={}\nend_min={}\npayday={}\npill_mode={}\nquote_offset={}\n",
            self.monthly_salary,
            self.rest_mode,
            self.start_hour,
            self.start_min,
            self.end_hour,
            self.end_min,
            self.payday,
            self.pill_mode,
            self.quote_offset
        );
        let _ = crate::model::atomic_write(&path, body.as_bytes());
    }
}

fn store() -> &'static Mutex<WonangConfig> {
    static STORE: OnceLock<Mutex<WonangConfig>> = OnceLock::new();
    STORE.get_or_init(|| Mutex::new(WonangConfig::load_from_disk()))
}

pub fn get_config() -> WonangConfig {
    store().lock().unwrap().clone()
}

pub fn update_config(f: impl FnOnce(&mut WonangConfig)) {
    let mut guard = store().lock().unwrap();
    let before = guard.clone();
    f(&mut guard);
    if *guard != before {
        guard.save_to_disk();
    }
}

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum WorkState {
    RestDay,
    BeforeWork,
    Working,
    AfterWork,
}

pub struct CalcResult {
    pub state: WorkState,
    pub daily_salary: f64,
    pub earned_today: f64,
    pub per_second: f64,
    pub progress: f32,
    pub remain_secs: u64,
    pub days_to_payday: u32,
}

pub fn calculate(cfg: &WonangConfig) -> CalcResult {
    let now = Local::now();
    let daily_salary = cfg.monthly_salary / cfg.work_days_per_month();

    let weekday = now.weekday().num_days_from_monday(); // 0 = Mon .. 6 = Sun
    let is_rest_day = match cfg.rest_mode {
        0 => weekday >= 5, // Sat, Sun
        1 | 2 => weekday == 6, // Sun
        _ => false,
    };

    let start_sec = (cfg.start_hour * 3600 + cfg.start_min * 60) as f64;
    let mut end_sec = (cfg.end_hour * 3600 + cfg.end_min * 60) as f64;
    if end_sec <= start_sec {
        end_sec = start_sec + 3600.0;
    }
    let work_span = (end_sec - start_sec).max(60.0);
    let per_second = daily_salary / work_span;

    let now_sec = (now.hour() * 3600 + now.minute() * 60 + now.second()) as f64
        + (now.nanosecond() as f64 / 1_000_000_000.0);

    let (state, earned_today, progress, remain_secs) = if is_rest_day {
        (WorkState::RestDay, 0.0, 0.0, 0)
    } else if now_sec < start_sec {
        (WorkState::BeforeWork, 0.0, 0.0, (end_sec - start_sec) as u64)
    } else if now_sec < end_sec {
        let elapsed = now_sec - start_sec;
        let prog = (elapsed / work_span).clamp(0.0, 1.0);
        (
            WorkState::Working,
            daily_salary * prog,
            prog as f32,
            (end_sec - now_sec).ceil().max(0.0) as u64,
        )
    } else {
        (WorkState::AfterWork, daily_salary, 1.0, 0)
    };

    let today = now.date_naive();
    let days_to_payday = days_until_payday(today, cfg.payday);

    CalcResult {
        state,
        daily_salary,
        earned_today,
        per_second,
        progress,
        remain_secs,
        days_to_payday,
    }
}

fn days_until_payday(today: NaiveDate, payday: u32) -> u32 {
    let year = today.year();
    let month = today.month();
    let target_this_month = clamp_day(year, month, payday);
    if target_this_month >= today {
        return (target_this_month - today).num_days().max(0) as u32;
    }
    let (next_y, next_m) = if month == 12 { (year + 1, 1) } else { (year, month + 1) };
    let target_next = clamp_day(next_y, next_m, payday);
    (target_next - today).num_days().max(0) as u32
}

fn clamp_day(year: i32, month: u32, day: u32) -> NaiveDate {
    for d in (1..=day.min(31)).rev() {
        if let Some(date) = NaiveDate::from_ymd_opt(year, month, d) {
            return date;
        }
    }
    NaiveDate::from_ymd_opt(year, month, 1).unwrap()
}

/// 当开启了「收起时显示今日窝囊费」时，返回药丸上要显示的文字（替代或轮播时间）。
pub fn pill_override_text(t: f64) -> Option<String> {
    let cfg = get_config();
    match cfg.pill_mode {
        0 => None,
        1 => {
            if ((t as u64) / 5) % 2 == 1 {
                let res = calculate(&cfg);
                Some(format!("¥{:.1}", res.earned_today))
            } else {
                None
            }
        }
        _ => {
            let res = calculate(&cfg);
            Some(format!("¥{:.1}", res.earned_today))
        }
    }
}

pub fn pill_needs_wide_clock() -> bool {
    get_config().pill_mode != 0
}

pub fn draw_sidebar_icon(ui: &mut egui::Ui, rect: Rect) {
    ui.painter().rect_filled(rect, 6.5, Color32::from_rgb(218, 148, 28));
    ui.painter().rect_stroke(
        rect.shrink(0.5),
        6.0,
        egui::Stroke::new(1.0_f32, Color32::from_white_alpha(40)),
        egui::StrokeKind::Inside,
    );
    ui.painter().text(
        rect.center(),
        egui::Align2::CENTER_CENTER,
        "¥",
        egui::FontId::proportional(15.0),
        Color32::WHITE,
    );
}

impl App {
    pub(crate) fn page_wonangfei(&mut self, c: &Card, _env: &Env) {
        let cfg = get_config();
        let res = calculate(&cfg);

        // 顶部状态胶囊（标题右侧）
        let (badge_text, badge_bg, badge_fg) = match res.state {
            WorkState::Working => (
                format!("搬砖受气中 · 秒入 ¥{:.3}", res.per_second),
                GOLD_DIM,
                GOLD,
            ),
            WorkState::BeforeWork => (
                format!("{:02}:{:02} 准时开挣窝囊费", cfg.start_hour, cfg.start_min),
                Color32::from_rgb(38, 42, 52),
                theme::GRAY,
            ),
            WorkState::AfterWork => (
                "今日窝囊费已全额到账 🎉".to_string(),
                Color32::from_rgb(24, 62, 42),
                theme::GREEN,
            ),
            WorkState::RestDay => (
                "休息日 · 今日免受窝囊气 ☕".to_string(),
                Color32::from_rgb(38, 48, 62),
                theme::BLUE,
            ),
        };
        let bw = c.text_w(&badge_text, 9.5, W::Semibold) + 14.0;
        c.fill(112.0, 11.0, bw, 17.5, 8.5, badge_bg);
        c.centered_text(112.0 + bw / 2.0, 19.8, &badge_text, 9.5, W::Semibold, badge_fg, H::Center);

        // 左侧主金额展示区
        c.text(18.0, 46.0, "今日已挣窝囊费", 10.5, W::Regular, theme::GRAY, H::Left);
        let money_text = if res.state == WorkState::Working {
            format!("¥ {:.3}", res.earned_today)
        } else {
            format!("¥ {:.2}", res.earned_today)
        };
        c.text(18.0, 74.0, &money_text, 25.0, W::Bold, GOLD, H::Left);

        // 进度条
        let bar_x = 18.0;
        let bar_y = 86.0;
        let bar_w = 226.0;
        let bar_h = 6.0;
        c.fill(bar_x, bar_y, bar_w, bar_h, 3.0, Color32::from_rgb(38, 38, 42));
        if res.progress > 0.0 {
            let fill_w = (bar_w * res.progress).max(bar_h);
            let fill_col = if res.state == WorkState::AfterWork { theme::GREEN } else { GOLD };
            c.fill(bar_x, bar_y, fill_w, bar_h, 3.0, fill_col);
        }
        let pct_text = format!("{:.1}%", res.progress * 100.0);
        c.text(bar_x + bar_w, 74.0, &pct_text, 10.5, W::Semibold, theme::GRAY, H::Right);

        // 底部诙谐吐槽语录（可点击切换下一句）
        let quote_idx = ((self.t as usize / 10) + cfg.quote_offset) % QUOTES.len();
        let quote = c.fit(QUOTES[quote_idx], 10.0, W::Regular, 228.0);
        let quote_hit = c.hit(16.0, 97.0, 232.0, 22.0, "wonang-quote").on_hover_text("点击换一句打工吐槽");
        let quote_col = if quote_hit.hovered() { theme::WHITE } else { Color32::from_gray(172) };
        c.text(18.0, 111.0, &quote, 10.0, W::Regular, quote_col, H::Left);
        if quote_hit.clicked() {
            update_config(|c| c.quote_offset = c.quote_offset.wrapping_add(1));
        }

        // 右侧数据小卡片
        let rx = 256.0;
        let ry = 34.0;
        let rw = 146.0;
        let rh = 84.0;
        c.fill(rx, ry, rw, rh, 10.0, Color32::from_rgb(27, 27, 31));

        // 1. 距离下班
        c.text(rx + 10.0, ry + 20.0, "距离下班", 10.0, W::Regular, theme::GRAY, H::Left);
        let off_text = match res.state {
            WorkState::Working => {
                let h = res.remain_secs / 3600;
                let m = (res.remain_secs % 3600) / 60;
                let s = res.remain_secs % 60;
                format!("{h:02}:{m:02}:{s:02}")
            }
            WorkState::BeforeWork => "尚未开工".to_string(),
            WorkState::AfterWork => "快跑别加班".to_string(),
            WorkState::RestDay => "今日不营业".to_string(),
        };
        c.text(rx + rw - 10.0, ry + 20.0, &off_text, 10.5, W::Semibold, theme::WHITE, H::Right);

        c.seg((rx + 10.0, ry + 28.0), (rx + rw - 10.0, ry + 28.0), 0.6, Color32::from_gray(40));

        // 2. 距离发薪
        c.text(rx + 10.0, ry + 46.0, "距离发粮", 10.0, W::Regular, theme::GRAY, H::Left);
        let pay_text = if res.days_to_payday == 0 {
            "今天发窝囊费!".to_string()
        } else {
            format!("还有 {} 天", res.days_to_payday)
        };
        let pay_col = if res.days_to_payday <= 3 { GOLD } else { theme::WHITE };
        c.text(rx + rw - 10.0, ry + 46.0, &pay_text, 10.5, W::Semibold, pay_col, H::Right);

        c.seg((rx + 10.0, ry + 54.0), (rx + rw - 10.0, ry + 54.0), 0.6, Color32::from_gray(40));

        // 3. 日均窝囊费
        c.text(rx + 10.0, ry + 72.0, &format!("日薪({})", cfg.rest_label()), 10.0, W::Regular, theme::GRAY, H::Left);
        c.text(rx + rw - 10.0, ry + 72.0, &format!("¥{:.0}/天", res.daily_salary), 10.5, W::Semibold, GOLD, H::Right);
    }
}

pub fn settings_ui(app: &mut App, ui: &mut egui::Ui, ctx: &egui::Context) {
    use crate::extras::{setting_row, settings_card, settings_control_row, settings_label};

    let mut cfg = get_config();
    let before = cfg.clone();

    let res = calculate(&cfg);
    settings_label(ui, "实时窝囊费预览");
    settings_card(ui, |ui| {
        ui.horizontal(|ui| {
            ui.vertical(|ui| {
                ui.label(RichText::new(format!("今日已挣：¥ {:.2}", res.earned_today)).size(16.0).strong().color(GOLD));
                ui.label(
                    RichText::new(format!(
                        "折合日薪：¥ {:.2} / 天（{}，月均 {} 天） · 距离 {} 号发薪还有 {} 天",
                        res.daily_salary,
                        cfg.rest_label(),
                        cfg.work_days_per_month(),
                        cfg.payday,
                        res.days_to_payday
                    ))
                    .size(12.0),
                );
            });
        });
    });

    settings_label(ui, "显示位置与开关");
    settings_card(ui, |ui| {
        let mut page_on = app.settings.visible_pages[8];
        let can_change = !page_on || app.settings.visible_pages.iter().filter(|enabled| **enabled).count() > 1;
        ui.add_enabled_ui(can_change, |ui| {
            setting_row(
                ui,
                "在灵动岛展开页面显示「今日窝囊费」",
                "展开灵动岛时可切换到「今日窝囊费」看板实时查看入账金额",
                &mut page_on,
            );
        });
        if page_on != app.settings.visible_pages[8] {
            app.set_page_visible(8, page_on);
        }
        ui.separator();
        settings_control_row(ui, "收起时显示", 84.0, |ui| {
            ui.horizontal(|ui| {
                for (mode, label) in [(0u8, "仅展开时显示"), (1u8, "与时间轮播(5秒)"), (2u8, "收起时常驻")] {
                    if ui.selectable_label(cfg.pill_mode == mode, label).clicked() {
                        cfg.pill_mode = mode;
                    }
                }
            })
            .response
        });
    });

    settings_label(ui, "打工人参数设置");
    settings_card(ui, |ui| {
        settings_control_row(ui, "税前/到手月薪", 96.0, |ui| {
            ui.horizontal(|ui| {
                ui.add(
                    egui::DragValue::new(&mut cfg.monthly_salary)
                        .range(500.0..=1_000_000.0)
                        .speed(100.0)
                        .prefix("¥ ")
                        .suffix(" / 月")
                        .fixed_decimals(0),
                );
                for preset in [6000.0, 10000.0, 15000.0, 20000.0] {
                    if ui.small_button(format!("¥{}", preset as u32)).clicked() {
                        cfg.monthly_salary = preset;
                    }
                }
            })
            .response
        });
        ui.separator();
        settings_control_row(ui, "休假制度", 96.0, |ui| {
            ui.horizontal(|ui| {
                for (mode, label) in [
                    (0u8, "双休 (21.75天)"),
                    (1u8, "大小周 (24天)"),
                    (2u8, "单休 (26天)"),
                    (3u8, "全勤 (30天)"),
                ] {
                    if ui.selectable_label(cfg.rest_mode == mode, label).clicked() {
                        cfg.rest_mode = mode;
                    }
                }
            })
            .response
        });
        ui.separator();
        settings_control_row(ui, "上班时间", 96.0, |ui| {
            ui.horizontal(|ui| {
                ui.add(egui::DragValue::new(&mut cfg.start_hour).range(0..=23).suffix(" 时"));
                ui.label(":");
                ui.add(egui::DragValue::new(&mut cfg.start_min).range(0..=59).suffix(" 分"));
            })
            .response
        });
        ui.separator();
        settings_control_row(ui, "下班时间", 96.0, |ui| {
            ui.horizontal(|ui| {
                ui.add(egui::DragValue::new(&mut cfg.end_hour).range(0..=23).suffix(" 时"));
                ui.label(":");
                ui.add(egui::DragValue::new(&mut cfg.end_min).range(0..=59).suffix(" 分"));
            })
            .response
        });
        ui.separator();
        settings_control_row(ui, "每月发薪日", 96.0, |ui| {
            ui.horizontal(|ui| {
                ui.add(egui::DragValue::new(&mut cfg.payday).range(1..=31).prefix("每月 ").suffix(" 号"));
                for d in [5u32, 10, 15, 25, 30] {
                    if ui.small_button(format!("{d}号")).clicked() {
                        cfg.payday = d;
                    }
                }
            })
            .response
        });
    });

    if cfg != before {
        update_config(|c| *c = cfg);
        ctx.request_repaint();
    }
}
