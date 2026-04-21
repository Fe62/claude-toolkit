-- import_iif.applescript
-- Usage: osascript import_iif.applescript /path/to/payroll_MMDD.iif
-- QuickBooks must be open. Uses shell `open -a` to hand the IIF file
-- directly to QB (avoids file dialog navigation), then dismisses the
-- backup warning ("No") and success confirmation ("OK").

on run argv
    if (count of argv) < 1 then
        error "Usage: osascript import_iif.applescript /path/to/file.iif"
    end if
    set iifPath to item 1 of argv
    importIIF(iifPath)
end run

on importIIF(iifPath)
    -- Hand the IIF file to QuickBooks via the OS file association
    do shell script "open -a 'QuickBooks 2024' " & quoted form of iifPath
    delay 3

    -- Handle up to 3 dialogs: backup warning, success confirmation, etc.
    tell application "System Events"
        tell process "QuickBooks"
            set frontmost to true
            repeat 4 times
                delay 1.5
                try
                    set fw to first window
                    set btns to name of every button of fw
                    if "No" is in btns then
                        click button "No" of fw       -- "back up before import?" → No
                        delay 1
                    else if "OK" is in btns then
                        click button "OK" of fw       -- success / info dialog → OK
                        delay 1
                    end if
                end try
            end repeat
        end tell
    end tell
end importIIF
