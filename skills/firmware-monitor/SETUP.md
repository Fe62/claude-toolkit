# Firmware Monitor — Setup Guide

One-time setup for the Direct Lighting iMac.

---

## Step 1 — Copy files

```bash
cp -r firmware-monitor ~/payroll/
cd ~/payroll/firmware-monitor
```

---

## Step 2 — Install Python dependencies

```bash
pip3 install requests beautifulsoup4
```

---

## Step 3 — Google API key (for Cerise)

The Cerise firmware lives in a public Google Drive folder.
Monitoring it requires a free Google Cloud API key.

1. Go to https://console.cloud.google.com/
2. Create a new project (e.g. "firmware-monitor")
3. Go to **APIs & Services → Library**
4. Search for **Google Drive API** and enable it
5. Go to **APIs & Services → Credentials → Create Credentials → API Key**
6. Copy the key
7. Open `manufacturers.json` and replace `YOUR_GOOGLE_API_KEY_HERE` with your key

No billing required — the Drive API free tier is more than sufficient for
daily polling of a single folder.

---

## Step 4 — Verify sendmail / Postfix

macOS ships with Postfix but it may not be running or configured to relay outbound mail.

### Test first:
```bash
echo "Subject: firmware monitor test" | sendmail flint@directlighting.net
```

Check if it arrives within a few minutes.

### If it doesn't arrive — configure Postfix relay via Gmail:

1. Create a Gmail App Password:
   - Google Account → Security → 2-Step Verification → App passwords
   - Create one for "Mail" / "Mac"

2. Create `/etc/postfix/sasl_passwd`:
   ```
   [smtp.gmail.com]:587 your.gmail@gmail.com:YOUR_APP_PASSWORD
   ```

3. Set permissions and hash:
   ```bash
   sudo chmod 600 /etc/postfix/sasl_passwd
   sudo postmap /etc/postfix/sasl_passwd
   ```

4. Edit `/etc/postfix/main.cf` — add/update these lines:
   ```
   relayhost = [smtp.gmail.com]:587
   smtp_sasl_auth_enable = yes
   smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
   smtp_sasl_security_options = noanonymous
   smtp_tls_security_level = encrypt
   smtp_tls_CAfile = /etc/ssl/cert.pem
   ```

5. Restart Postfix:
   ```bash
   sudo postfix reload
   ```

6. Test again.

---

## Step 5 — First run (baseline)

```bash
cd ~/payroll/firmware-monitor
python3 check_firmware.py
```

This records current state — **no alerts will fire on first run**.
Inspect `state.json` to confirm all 8 entries were captured.

If any entry shows `ERROR`, check the log and fix before enabling cron.

---

## Step 6 — Enable cron

```bash
crontab -e
```

Add (replace `YOURUSERNAME`):
```
0 8 * * * cd /Users/YOURUSERNAME/payroll/firmware-monitor && /usr/bin/python3 check_firmware.py >> firmware_monitor.log 2>&1
```

Verify it's set:
```bash
crontab -l
```

---

## Done

The monitor will run every morning at 8am and email the team if anything changes.
Check `firmware_monitor.log` periodically to confirm it's running cleanly.
