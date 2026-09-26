# 🛡️ Aegis AI — Open WebUI Implementation Guide
**Target Instance**: [https://chat.exac.site](https://chat.exac.site)  
**Brand**: Aegis AI — Enterprise Artificial Intelligence Platform  
**Tagline**: *Your Intelligent AI Guardian*

---

## 📌 Cara Pasang Theme Aegis AI pada Open WebUI

Ada **3 Cara** untuk mengimplementasikan Aegis AI ke instance Open WebUI Anda di `https://chat.exac.site`:

### 🔹 Metode 1: Melalui Admin Panel Open WebUI (Paling Cepat & Tanpa Restart)
1. Buka browser dan login ke Open WebUI dengan akun **Admin**:
   👉 `https://chat.exac.site/admin/settings`
2. Masuk ke menu **Admin Settings** ➜ **Interface**.
3. Cari form **Custom CSS**:
   - Buka file [`aegis-openwebui-theme.css`](./aegis-openwebui-theme.css).
   - Copy seluruh isinya.
   - Paste ke dalam kotak **Custom CSS** di Open WebUI.
4. Pada kolom **Custom App Title**, ganti menjadi:
   `Aegis AI`
5. Pada kolom **Custom App Description**, masukkan:
   `Your Intelligent AI Guardian — Enterprise Artificial Intelligence Platform`
6. Upload atau set URL **Custom Logo**:
   - Gunakan file SVG logo yang telah disiapkan di `assets/logos/aegis-logo-primary.svg` atau `aegis-logo-symbol.svg`.
7. Klik **Save**.
8. Refresh halaman (`Ctrl + F5` atau `Cmd + Shift + R`). Tampilan Open WebUI Anda seketika berubah menjadi Aegis AI Enterprise!

---

### 🔹 Metode 2: Melalui File Server / Docker Volume (Permanen)
Jika Anda meng-host Open WebUI menggunakan Docker:
1. Copy file CSS ini ke static directory container:
   ```bash
   docker cp aegis-openwebui-theme.css open-webui:/app/backend/open_webui/static/custom.css
   ```
2. Atau mount file CSS melalui `docker-compose.yml`:
   ```yaml
   volumes:
     - ./openwebui/aegis-openwebui-theme.css:/app/backend/open_webui/static/custom.css:ro
     - ./assets/logos/aegis-favicon.svg:/app/backend/open_webui/static/favicon.svg:ro
     - ./assets/logos/aegis-logo-symbol.svg:/app/backend/open_webui/static/logo.svg:ro
   ```

---

### 🔹 Metode 3: Menggunakan Aegis AI Enterprise Portal (Landing Page Frontend)
Folder ini dilengkapi dengan **Enterprise Landing Page** (`index.html`) yang siap dideploy sebagai muka utama:
- Pengguna yang mengunjungi domain utama disambut oleh Landing Page futuristik berteknologi tinggi dengan neural particle animation, showcase kapabilitas AI, ekosistem model, dan fitur enterprise.
- Klik tombol **"Start Conversation"** atau **"Login"** langsung mengarahkan pengguna ke sesi chat `https://chat.exac.site` atau membuka chat workspace bridge.
- Dapat dideploy dengan Nginx, Cloudflare Pages, Vercel, ataupun disatukan ke reverse proxy Open WebUI.

---

## 🎨 Asset Check-List
- Primary Logo: `assets/logos/aegis-logo-primary.svg`
- Symbol / Favicon: `assets/logos/aegis-favicon.svg` & `assets/logos/aegis-logo-symbol.svg`
- High-Res Mockups: `assets/images/aegis_landing_mockup.jpg`, `aegis_dashboard_mockup.jpg`, `aegis_app_icon.jpg`
- Standalone Portal: `index.html`
