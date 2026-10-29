# Dernek Yazılımı web sitesi

https://dernekyazilimi.github.io/

Türkçe, mobil uyumlu statik tanıtım ve dokümantasyon sitesi. Harici font, JavaScript veya Python paket bağımlılığı yoktur.

## Sayfalar

Ana sayfa, proje hakkında, modüller, entegrasyonlar, kurulum, katkı ve lisans.

İçerik uygulama deposunun README.md, INSTALLING.md, CONTRIBUTING.md, LICENSE / LICENSE.md ve CLAUDE.md belgelerinden editoryal olarak uyarlanmıştır. Kurulum bilgileri composer.json, package.json, .env.example ve config/modules.php ile karşılaştırılmıştır. Dahili sunucu adresleri ve operasyon bilgileri yayımlanmaz. Lisans metni aynen korunur.

## Düzenleme

1. `content/` altındaki sayfa içeriğini değiştirin.
2. Ortak başlık, navigasyon ve alt bilgi için `scripts/build.py` dosyasını düzenleyin.
3. `python3 scripts/build.py` çalıştırın.
4. `python3 scripts/check.py` ile site içi bağlantıları kontrol edin.
5. `python3 -m http.server 8089` ile yerel önizlemeyi açın.
6. Kaynak ve üretilmiş HTML dosyalarını birlikte commit edin.

GitHub Pages, `main` dalının kök dizininden yayın yapar. Üretilmiş HTML dosyaları depoda bulunduğundan Pages tarafında özel derleme gerekmez.

Kaynak proje: https://github.com/lkdtr/dernekyazilimi

## SEO

`scripts/build.py`, yedi sayfanın canonical adreslerini, sayfaya özgü başlık/açıklamalarını, Open Graph ve X kartlarını, WebSite/WebPage ve alt sayfa BreadcrumbList JSON-LD verilerini üretir. Sitemap aynı sayfa listesinden türetilir; robots.txt sitemap adresini duyurur. İçerik kaynak klasörleri tarama dışında, sayfalar ve görsel varlıklar taramaya açıktır.

Paylaşım görseli: `assets/seo/sosyal-paylasim.png` (1200×630). `scripts/check.py` sitemap kapsamını, robots erişimini, meta etiketlerini, görsel boyutlarını ve JSON-LD tutarlılığını kontrol eder. Search Console kaydı veya arama motoruna manuel gönderim yapılmamıştır.
