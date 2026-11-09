#!/usr/bin/env python3
"""
Automatically rebrand upstream Renly1994/xiaotang-daozai into WELL岛 (wellshijian/welldao).
Idempotent: can be run on upstream checkout or an already-rebranded checkout.
"""
import os
import re
import shutil

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Restore custom WELL icons over upstream icons
brand_ico = os.path.join(base_dir, "assets", "well-brand.ico")
brand_png = os.path.join(base_dir, "assets", "well-brand.png")
if os.path.exists(brand_ico):
    shutil.copyfile(brand_ico, os.path.join(base_dir, "assets", "daozai.ico"))
if os.path.exists(brand_png):
    shutil.copyfile(brand_png, os.path.join(base_dir, "assets", "daozai-logo.png"))

def replace_in_file(rel_path, pairs, encoding="utf-8"):
    path = os.path.join(base_dir, rel_path)
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()
    orig = content
    for item in pairs:
        if callable(item):
            content = item(content)
        else:
            old, new = item
            content = content.replace(old, new)
    if content != orig:
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        print(f"Updated {rel_path}")

# 2. Cargo.toml & app.rc (including +1 patch version bump from upstream so WELL岛 custom releases never collide with upstream tags)
cargo_path = os.path.join(base_dir, "Cargo.toml")
with open(cargo_path, "r", encoding="utf-8-sig") as f:
    cargo_raw = f.read()

is_fresh_upstream = 'name = "daozai"' in cargo_raw
ver_match = re.search(r'(?m)^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', cargo_raw)
if ver_match and (is_fresh_upstream or ver_match.group(0).endswith('"0.6.63"')):
    maj, mino, pat = int(ver_match.group(1)), int(ver_match.group(2)), int(ver_match.group(3))
    old_ver = f"{maj}.{mino}.{pat}"
    new_ver = f"{maj}.{mino}.{pat + 1}"
    old_rc_ver = f"{maj},{mino},{pat},0"
    new_rc_ver = f"{maj},{mino},{pat + 1},0"
else:
    old_ver = new_ver = old_rc_ver = new_rc_ver = None

replace_in_file("Cargo.toml", [
    (lambda s: s.replace(f'version = "{old_ver}"', f'version = "{new_ver}"') if old_ver else s),
    (lambda s: re.sub(r'(\[package\]\s+name\s*=\s*)"daozai"', r'\1"wellshijian"', s)),
    ('default-run = "daozai"', 'default-run = "wellshijian"'),
    (lambda s: re.sub(r'(\[\[bin\]\]\s+name\s*=\s*)"daozai"', r'\1"wellshijian"', s)),
    ('description = "岛仔：Windows 顶部的桌面伙伴与信息岛"', 'description = "WELL岛：Windows 顶部的桌面伙伴与信息岛"'),
    ('description = "wellshijian：Windows 顶部的桌面伙伴与信息岛"', 'description = "WELL岛：Windows 顶部的桌面伙伴与信息岛"'),
    ('Renly1994/xiaotang-daozai', 'wellshijian/welldao'),
])

# 3. app.rc
replace_in_file("app.rc", [
    (lambda s: s.replace(old_rc_ver, new_rc_ver).replace(f'"{old_ver}"', f'"{new_ver}"') if old_ver else s),
    ('VALUE "FileDescription", "岛仔"', 'VALUE "FileDescription", "WELL岛"'),
    ('VALUE "FileDescription", "wellshijian"', 'VALUE "FileDescription", "WELL岛"'),
    ('VALUE "InternalName", "Daozai"', 'VALUE "InternalName", "wellshijian"'),
    ('VALUE "OriginalFilename", "daozai.exe"', 'VALUE "OriginalFilename", "wellshijian.exe"'),
    ('VALUE "ProductName", "岛仔 Daozai"', 'VALUE "ProductName", "WELL岛"'),
    ('VALUE "ProductName", "wellshijian"', 'VALUE "ProductName", "WELL岛"'),
])

# 4. src/model.rs
replace_in_file("src/model.rs", [
    ('env_dir("APPDATA").join("Daozai")', 'env_dir("APPDATA").join("wellshijian")'),
])

# 5. src/tray.rs
replace_in_file("src/tray.rs", [
    ('const RUN_VALUE: PCWSTR = w!("Daozai");', 'const RUN_VALUE: PCWSTR = w!("wellshijian");'),
    ('const MUTEX_NAME: PCWSTR = w!("Local\\\\Daozai.SingleInstance");', 'const MUTEX_NAME: PCWSTR = w!("Local\\\\wellshijian.SingleInstance");'),
    ('let class = w!("DaozaiTray");', 'let class = w!("wellshijianTray");'),
    ('FindWindowW(w!("DaozaiTray")', 'FindWindowW(w!("wellshijianTray")'),
    ('w!("岛仔托盘")', 'w!("WELL岛托盘")'),
    ('w!("wellshijian托盘")', 'w!("WELL岛托盘")'),
    ('["开机启动", "吉祥物", "极简刘海", "关于岛仔", "退出", "设置…"]', '["开机启动", "吉祥物", "极简刘海", "关于 WELL岛", "退出", "设置…"]'),
    ('["开机启动", "吉祥物", "极简刘海", "关于 wellshijian", "退出", "设置…"]', '["开机启动", "吉祥物", "极简刘海", "关于 WELL岛", "退出", "设置…"]'),
    ('fill_tip(&mut nid.szTip, "岛仔");', 'fill_tip(&mut nid.szTip, "WELL岛");'),
    ('fill_tip(&mut nid.szTip, "wellshijian");', 'fill_tip(&mut nid.szTip, "WELL岛");'),
    ('"岛仔 {}\\n\\nWindows 桌面灵动岛小助手\\n退出请右键托盘图标，选择「退出」。"', '"WELL岛 {}\\n\\nWindows 桌面灵动岛小助手\\n退出请右键托盘图标，选择「退出」。"'),
    ('"wellshijian {}\\n\\nWindows 桌面灵动岛小助手\\n退出请右键托盘图标，选择「退出」。"', '"WELL岛 {}\\n\\nWindows 桌面灵动岛小助手\\n退出请右键托盘图标，选择「退出」。"'),
    ('let title = wide("关于岛仔");', 'let title = wide("关于 WELL岛");'),
    ('let title = wide("关于 wellshijian");', 'let title = wide("关于 WELL岛");'),
    ('"关于岛仔"', '"关于 WELL岛"'),
    ('"关于 wellshijian"', '"关于 WELL岛"'),
])

# 6. src/main.rs
replace_in_file("src/main.rs", [
    ('.with_title("岛仔")', '.with_title("WELL岛")'),
    ('.with_title("wellshijian")', '.with_title("WELL岛")'),
    ('eframe::run_native("岛仔", opts', 'eframe::run_native("WELL岛", opts'),
    ('eframe::run_native("wellshijian", opts', 'eframe::run_native("WELL岛", opts'),
    ('diagnostics::report("岛仔启动或运行失败。"', 'diagnostics::report("WELL岛 启动或运行失败。"'),
    ('diagnostics::report("wellshijian 启动或运行失败。"', 'diagnostics::report("WELL岛 启动或运行失败。"'),
])

# 7. src/extras.rs
replace_in_file("src/extras.rs", [
    ('with_title("岛仔设置")', 'with_title("WELL岛 设置")'),
    ('with_title("wellshijian 设置")', 'with_title("WELL岛 设置")'),
    ('setting_row(ui,"开机启动","登录 Windows 时自动打开岛仔"', 'setting_row(ui,"开机启动","登录 Windows 时自动打开 WELL岛"'),
    ('setting_row(ui,"开机启动","登录 Windows 时自动打开 wellshijian"', 'setting_row(ui,"开机启动","登录 Windows 时自动打开 WELL岛"'),
    ('c.text(42.0,116.0,"岛仔收起时常驻；极简模式保留细线"', 'c.text(42.0,116.0,"WELL岛 收起时常驻；极简模式保留细线"'),
    ('c.text(42.0,116.0,"wellshijian 收起时常驻；极简模式保留细线"', 'c.text(42.0,116.0,"WELL岛 收起时常驻；极简模式保留细线"'),
    ('setting_row(ui,"岛仔吉祥物"', 'setting_row(ui,"WELL岛吉祥物"'),
    ('setting_row(ui,"岛仔提醒"', 'setting_row(ui,"WELL岛提醒"'),
    ('settings_label(ui,"岛仔 Daozai");', 'settings_label(ui,"WELL岛");'),
    ('settings_label(ui,"wellshijian");', 'settings_label(ui,"WELL岛");'),
    ('settings_label(ui,"支持作者");', ''),
    ('settings_card(ui,support_author);', 'if false { support_author(ui); }'),
])

# 8. src/app.rs
replace_in_file("src/app.rs", [
    ('_ => ("岛仔", "设置", theme::WHITE),', '_ => ("WELL岛", "设置", theme::WHITE),'),
    ('_ => ("wellshijian", "设置", theme::WHITE),', '_ => ("WELL岛", "设置", theme::WHITE),'),
])

# 9. src/mail.rs, calendar.rs, grok_quota.rs, lyrics.rs, diagnostics.rs, system.rs, mail_reader.rs
replace_in_file("src/mail.rs", [
    ('pub const SERVICE: &str = "Daozai.Mail";', 'pub const SERVICE: &str = "wellshijian.Mail";'),
    ('输入应用名称（例如：岛仔）', '输入应用名称（例如：WELL岛）'),
    ('输入应用名称（例如：wellshijian）', '输入应用名称（例如：WELL岛）'),
])
replace_in_file("src/calendar.rs", [
    ('pub const SERVICE: &str = "Daozai.Calendar";', 'pub const SERVICE: &str = "wellshijian.Calendar";'),
    ('concat!("Daozai/",env!("CARGO_PKG_VERSION"))', 'concat!("wellshijian/",env!("CARGO_PKG_VERSION"))'),
])
replace_in_file("src/grok_quota.rs", [
    ('keyring::Entry::new("Daozai.GrokBot",slot)', 'keyring::Entry::new("wellshijian.GrokBot",slot)'),
])
replace_in_file("src/lyrics.rs", [
    ('concat!("Daozai/",env!("CARGO_PKG_VERSION")," (Windows)")', 'concat!("wellshijian/",env!("CARGO_PKG_VERSION")," (Windows)")'),
])
replace_in_file("src/diagnostics.rs", [
    ('"岛仔 {}\\n系统：{} / {}\\n时间（Unix 秒）：{timestamp}\\n{title}\\n{details}\\n"', '"WELL岛 {}\\n系统：{} / {}\\n时间（Unix 秒）：{timestamp}\\n{title}\\n{details}\\n"'),
    ('"wellshijian {}\\n系统：{} / {}\\n时间（Unix 秒）：{timestamp}\\n{title}\\n{details}\\n"', '"WELL岛 {}\\n系统：{} / {}\\n时间（Unix 秒）：{timestamp}\\n{title}\\n{details}\\n"'),
    ('w!("岛仔")', 'w!("WELL岛")'),
    ('w!("wellshijian")', 'w!("WELL岛")'),
    ('report("岛仔发生异常，请重新启动。"', 'report("WELL岛 发生异常，请重新启动。"'),
    ('report("wellshijian 发生异常，请重新启动。"', 'report("WELL岛 发生异常，请重新启动。"'),
])
replace_in_file("src/system.rs", [
    ('if app != "岛仔" && !body.is_empty() {', 'if app != "WELL岛" && !body.is_empty() {'),
    ('if app != "wellshijian" && !body.is_empty() {', 'if app != "WELL岛" && !body.is_empty() {'),
])
replace_in_file("src/mail_reader.rs", [
    ('.with_title("邮件全文 · 岛仔")', '.with_title("邮件全文 · WELL岛")'),
    ('.with_title("邮件全文 · wellshijian")', '.with_title("邮件全文 · WELL岛")'),
])

# 10. src/updates.rs
replace_in_file("src/updates.rs", [
    ('Renly1994/xiaotang-daozai', 'wellshijian/welldao'),
    ('.with_title("岛仔更新")', '.with_title("WELL岛 更新")'),
    ('.with_title("wellshijian 更新")', '.with_title("WELL岛 更新")'),
    ('"岛仔有新版本了"', '"WELL岛 有新版本了"'),
    ('"wellshijian 有新版本了"', '"WELL岛 有新版本了"'),
    ('!= "岛仔更新"', '!= "WELL岛 更新"'),
    ('!= "wellshijian 更新"', '!= "WELL岛 更新"'),
    ('.join("Daozai/Updates")', '.join("wellshijian/Updates")'),
    ('let name = format!("Daozai-v{}-windows-x64.zip", tag.trim_start_matches(\'v\'));', 'let name = "wellshijian-portable.zip".to_string();'),
])

# 11. installer/update.ps1, setup.nsi, install.ps1, uninstall.ps1
replace_in_file("installer/update.ps1", [
    ("Join-Path $env:LOCALAPPDATA 'Daozai\\Updates'", "Join-Path $env:LOCALAPPDATA 'wellshijian\\Updates'"),
    ("'daozai-update-'", "'wellshijian-update-'"),
    ("$name = 'Daozai-v' + $version + '-windows-x64/daozai.exe'\n        $entries = @($zip.Entries | Where-Object {$_.FullName.Replace('\\','/') -ceq $name})", "$entries = @($zip.Entries | Where-Object {$_.Name -ieq 'wellshijian.exe'})"),
    ("throw '更新包中缺少唯一的岛仔程序。'", "throw '更新包中缺少唯一的 WELL岛 程序。'"),
    ("throw '岛仔尚未退出，请稍后重试。'", "throw 'WELL岛 尚未退出，请稍后重试。'"),
    ("$key = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Daozai'", "$key = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\wellshijian'"),
    ("'岛仔更新'", "'WELL岛 更新'"),
])

replace_in_file("installer/setup.nsi", [
    ('!define APP_ID "Daozai"', '!define APP_ID "wellshijian"'),
    ('!define APP_NAME "岛仔"', '!define APP_NAME "WELL岛"'),
    ('!define APP_NAME "wellshijian"', '!define APP_NAME "WELL岛"'),
    ('VIAddVersionKey /LANG=2052 "LegalCopyright" "岛仔贡献者"', 'VIAddVersionKey /LANG=2052 "LegalCopyright" "WELL岛"'),
    ('VIAddVersionKey /LANG=2052 "LegalCopyright" "wellshijian"', 'VIAddVersionKey /LANG=2052 "LegalCopyright" "WELL岛"'),
    ('!define MUI_FINISHPAGE_TITLE "岛仔已安装"', '!define MUI_FINISHPAGE_TITLE "WELL岛 已安装"'),
    ('!define MUI_FINISHPAGE_TITLE "wellshijian 已安装"', '!define MUI_FINISHPAGE_TITLE "WELL岛 已安装"'),
    ('!define MUI_FINISHPAGE_RUN "$INSTDIR\\daozai.exe"', '!define MUI_FINISHPAGE_RUN "$INSTDIR\\wellshijian.exe"'),
    ('!define MUI_FINISHPAGE_RUN_TEXT "打开岛仔"', '!define MUI_FINISHPAGE_RUN_TEXT "打开 WELL岛"'),
    ('!define MUI_FINISHPAGE_RUN_TEXT "打开 wellshijian"', '!define MUI_FINISHPAGE_RUN_TEXT "打开 WELL岛"'),
    ('!define MUI_UNCONFIRMPAGE_TEXT_TOP "将卸载岛仔。设置、待办和连接记录会保留，重新安装后仍可使用。"', '!define MUI_UNCONFIRMPAGE_TEXT_TOP "将卸载 WELL岛。设置、待办和连接记录会保留，重新安装后仍可使用。"'),
    ('!define MUI_UNCONFIRMPAGE_TEXT_TOP "将卸载 wellshijian。设置、待办和连接记录会保留，重新安装后仍可使用。"', '!define MUI_UNCONFIRMPAGE_TEXT_TOP "将卸载 WELL岛。设置、待办和连接记录会保留，重新安装后仍可使用。"'),
    ('BrandingText "岛仔 · Daozai"', 'BrandingText "WELL岛"'),
    ('BrandingText "wellshijian"', 'BrandingText "WELL岛"'),
    ('"欢迎使用岛仔"', '"欢迎使用 WELL岛"'),
    ('"欢迎使用 wellshijian"', '"欢迎使用 WELL岛"'),
    ('"选择岛仔安装文件夹"', '"选择 WELL岛 安装文件夹"'),
    ('"选择 wellshijian 安装文件夹"', '"选择 WELL岛 安装文件夹"'),
    ('"岛仔需要 Windows 10 或 Windows 11 的 64 位系统。"', '"WELL岛 需要 Windows 10 或 Windows 11 的 64 位系统。"'),
    ('"wellshijian 需要 Windows 10 或 Windows 11 的 64 位系统。"', '"WELL岛 需要 Windows 10 或 Windows 11 的 64 位系统。"'),
    ('"岛仔需要 Windows 10 或 Windows 11。"', '"WELL岛 需要 Windows 10 或 Windows 11。"'),
    ('"wellshijian 需要 Windows 10 或 Windows 11。"', '"WELL岛 需要 Windows 10 或 Windows 11。"'),
    ('File /oname=daozai.exe "${SOURCE_EXE}"', 'File /oname=wellshijian.exe "${SOURCE_EXE}"'),
    ('CreateShortcut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\daozai.exe"', 'CreateShortcut "$DESKTOP\\${APP_NAME}.lnk" "$INSTDIR\\wellshijian.exe"'),
    ('WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APP_ID}" \'"$INSTDIR\\daozai.exe"\'', 'WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APP_ID}" \'"$INSTDIR\\wellshijian.exe"\''),
    ('CreateShortcut "$SMPROGRAMS\\${APP_NAME}.lnk" "$INSTDIR\\daozai.exe"', 'CreateShortcut "$SMPROGRAMS\\${APP_NAME}.lnk" "$INSTDIR\\wellshijian.exe"'),
    ('CreateShortcut "$SMPROGRAMS\\${APP_NAME}设置.lnk" "$INSTDIR\\daozai.exe" "--settings"', 'CreateShortcut "$SMPROGRAMS\\${APP_NAME}设置.lnk" "$INSTDIR\\wellshijian.exe" "--settings"'),
    ('WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayName" "${APP_NAME} Daozai"', 'WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayName" "${APP_NAME}"'),
    ('WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "岛仔"', 'WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "WELL岛"'),
    ('WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "wellshijian"', 'WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "WELL岛"'),
    ('WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\\daozai.exe,0"', 'WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\\wellshijian.exe,0"'),
    ('Delete "$INSTDIR\\daozai.exe"', 'Delete "$INSTDIR\\wellshijian.exe"'),
    ('Delete "$INSTDIR\\daozai-previous.exe"', 'Delete "$INSTDIR\\wellshijian-previous.exe"'),
    ('ReadRegStr $0 HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APP_ID}"\n  ${If} $0 == \'"$INSTDIR\\daozai.exe"\'', 'ReadRegStr $0 HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Run" "${APP_ID}"\n  ${If} $0 == \'"$INSTDIR\\wellshijian.exe"\''),
])

# 12. Inject 「今日窝囊费」 (wonangfei.rs) feature module & hooks
wonang_src = os.path.join(base_dir, "scripts", "wonangfei.rs")
wonang_dst = os.path.join(base_dir, "src", "wonangfei.rs")
if os.path.exists(wonang_src):
    shutil.copyfile(wonang_src, wonang_dst)

replace_in_file("src/lib.rs", [
    (lambda s: s if "pub mod wonangfei;" in s else s.replace("mod pages;", "pub mod wonangfei;\nmod pages;")),
])

replace_in_file("src/model.rs", [
    ("pub visible_pages: [bool; 8],", "pub visible_pages: [bool; 9],"),
    ("pub page_order: [usize; 8],", "pub page_order: [usize; 9],"),
    ("visible_pages: [true; 8], page_order: [0,1,2,3,4,5,6,7],", "visible_pages: [true; 9], page_order: [0,1,2,3,4,5,6,7,8],"),
    (
        'if order.len()==8 && (0..8).all(|page|order.contains(&page)) {\n                            s.page_order.copy_from_slice(&order);\n                        }',
        'if order.len()==9 && (0..9).all(|page|order.contains(&page)) {\n                            s.page_order.copy_from_slice(&order);\n                        } else if order.len()==8 && (0..8).all(|page|order.contains(&page)) {\n                            s.page_order[..8].copy_from_slice(&order);\n                            s.page_order[8]=8;\n                        }',
    ),
    ('"visible_pages" if (6..=8).contains(&v.len())', '"visible_pages" if (6..=9).contains(&v.len())'),
])

replace_in_file("src/app.rs", [
    (
        'pub(crate) const PAGE_NAMES: [&str; 8] = ["音乐", "专注", "饮水", "置物架", "待办", "邮箱", "AI 额度", "日程"];',
        'pub(crate) const PAGE_NAMES: [&str; 9] = ["音乐", "专注", "饮水", "置物架", "待办", "邮箱", "AI 额度", "日程", "今日窝囊费"];',
    ),
    ("dots: [Spring; 8],", "dots: [Spring; 9],"),
    ("self.settings_tab=[1,2,3,5,4,7,11,8][page];", "self.settings_tab=[1,2,3,5,4,7,11,8,12][page];"),
    ("if settings.clicked(){self.settings_tab=[1,2,3,5,4,7,11,8][self.page];self.open_settings();}", "if settings.clicked(){self.settings_tab=[1,2,3,5,4,7,11,8,12][self.page];self.open_settings();}"),
    ('6 => ("AI", "额度", theme::SOFT_GREEN),', '6 => ("AI", "额度", theme::SOFT_GREEN),\n            8 => ("今日", "窝囊费", Color32::from_rgb(255, 204, 72)),'),
    ("CALENDAR_PAGE => self.page_calendar(c,env),", "CALENDAR_PAGE => self.page_calendar(c,env),\n            8 => self.page_wonangfei(c, env),"),
    (
        "if self.settings.clock_period!=0 { layout.widen_clock(40.0); }",
        "if self.settings.clock_period!=0 { layout.widen_clock(40.0); } else if crate::wonangfei::pill_needs_wide_clock() { layout.widen_clock(24.0); }",
    ),
    (
        "let clock = self.settings.clock_text(&env.clock);",
        "let clock = if p < 0.25 { crate::wonangfei::pill_override_text(self.t).unwrap_or_else(|| self.settings.clock_text(&env.clock)) } else { self.settings.clock_text(&env.clock) };",
    ),
    (
        "|| self.notice.as_ref().is_some_and(|notice|notice.meeting.is_some());",
        "|| self.notice.as_ref().is_some_and(|notice|notice.meeting.is_some()) || (self.open && self.page == 8);",
    ),
])

replace_in_file("src/extras.rs", [
    (
        'const SETTINGS_GROUPS: [(&str,usize,usize);8] = [\n    ("常规",0,0), ("页面管理",10,10), ("音乐与歌词",1,1), ("专注与饮水",2,3),\n    ("待办与置物",4,5), ("通知、邮箱与日程",6,8), ("AI 额度",11,11), ("关于",9,9),\n];',
        'const SETTINGS_GROUPS: [(&str,usize,usize);9] = [\n    ("常规",0,0), ("页面管理",10,10), ("音乐与歌词",1,1), ("专注与饮水",2,3),\n    ("待办与置物",4,5), ("通知、邮箱与日程",6,8), ("AI 额度",11,11), ("今日窝囊费",12,12), ("关于",9,9),\n];',
    ),
    (
        "egui::Image::new(icon).paint_at(ui,icon_bg);",
        "if start==12 { crate::wonangfei::draw_sidebar_icon(ui,icon_bg); } else { egui::Image::new(icon).paint_at(ui,icon_bg); }",
    ),
    (
        'let titles=["常规","音乐与歌词","专注","饮水","待办","置物","通知","邮箱","日程","关于","页面管理","AI 额度"];\n                ui.label(egui::RichText::new(titles[self.settings_tab.min(11)])',
        'let titles=["常规","音乐与歌词","专注","饮水","待办","置物","通知","邮箱","日程","关于","页面管理","AI 额度","今日窝囊费"];\n                ui.label(egui::RichText::new(titles[self.settings_tab.min(12)])',
    ),
    (
        "11=>self.quota_settings(ui),",
        "12=>crate::wonangfei::settings_ui(self,ui,ctx),\n                    11=>self.quota_settings(ui),",
    ),
    (
        'let descriptions=["播放控制与同步歌词","番茄钟与休息计时","饮水记录与提醒","临时收纳文件位置","任务清单与到期提醒","邮件摘要与验证码","Agent 剩余额度和账号切换","月历、邮件邀请与工作日程"];',
        'let descriptions=["播放控制与同步歌词","番茄钟与休息计时","饮水记录与提醒","临时收纳文件位置","任务清单与到期提醒","邮件摘要与验证码","Agent 剩余额度和账号切换","月历、邮件邀请与工作日程","实时计算今日入账窝囊费与发薪日倒计时"];',
    ),
    (
        'setting_row(ui,"岛上歌词","收起时显示歌词，无歌词时显示封面和歌名",&mut self.settings.island_lyrics);',
        'setting_row(ui,"岛上歌词","收起时显示歌词，无歌词时显示封面和歌名",&mut self.settings.island_lyrics);\n                            ui.separator();\n                            let mut pill_on = crate::wonangfei::get_config().pill_mode != 0;\n                            setting_row(ui,"岛上窝囊费","收起时在顶部岛上轮播或常驻显示今日已挣窝囊费",&mut pill_on);\n                            if pill_on != (crate::wonangfei::get_config().pill_mode != 0) {\n                                crate::wonangfei::update_config(|c| c.pill_mode = if pill_on { 1 } else { 0 });\n                            }',
    ),
])

# 13. Fallback sweep across all src/*.rs and installer/* so any newly added upstream UI text with 岛仔/岛崽 is automatically replaced with WELL岛
for root_sub in ["src", "installer"]:
    folder = os.path.join(base_dir, root_sub)
    if not os.path.isdir(folder):
        continue
    for fname in os.listdir(folder):
        if fname == "ui_tests.rs":
            continue
        if fname.endswith((".rs", ".ps1", ".nsi")):
            replace_in_file(f"{root_sub}/{fname}", [
                ("岛仔 Daozai", "WELL岛"),
                ("岛仔", "WELL岛"),
                ("岛崽", "WELL岛"),
            ])

print("rebrand_welldao.py finished successfully.")
