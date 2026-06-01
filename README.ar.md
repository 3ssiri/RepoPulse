# RepoPulse

RepoPulse اداة سطر اوامر بلغة Python تفحص مستودعات GitHub وتنتج تقرير صحة واضح بدرجة من 100 مع توصيات عملية للتحسين.

## لماذا RepoPulse مهم؟

مشرفو المشاريع مفتوحة المصدر يكررون فحوصات كثيرة بين المستودعات: جودة README، الترخيص، الاختبارات، CI، النشاط، الملفات الحساسة بالاسم، والاساسيات الامنية. RepoPulse يحول هذه الفحوصات الى تقرير سريع يمكن تشغيله محليا او داخل CI.

## ما فائدة المشروع؟

يساعدك RepoPulse على معرفة جودة مستودع GitHub بسرعة:

- هل يوجد README جيد؟
- هل يوجد ترخيص؟
- هل توجد اختبارات؟
- هل توجد GitHub Actions؟
- هل توجد ملفات حساسة بالاسم؟
- هل بنية المشروع واضحة؟
- هل توجد توصيات أمنية او توصيات للتبعيات؟

## التثبيت

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
pip install -e .
```

للمطورين:

```bash
pip install -e ".[dev]"
```

## الاستخدام السريع

```bash
repopulse scan https://github.com/username/repository
```

تصدير Markdown:

```bash
repopulse scan https://github.com/username/repository --export report.md
```

تصدير JSON:

```bash
repopulse scan https://github.com/username/repository --format json --output report.json
```

فحص مستودع خاص:

```bash
repopulse scan https://github.com/username/private-repo --token YOUR_GITHUB_TOKEN
```

او عبر متغير البيئة:

```bash
GITHUB_TOKEN=YOUR_GITHUB_TOKEN repopulse scan https://github.com/username/private-repo
```

## نظام التقييم

| الفحص | النقاط |
|---|---:|
| README | 20 |
| License | 10 |
| .gitignore | 10 |
| Tests | 15 |
| GitHub Actions | 15 |
| Recent Activity | 10 |
| Sensitive Files | 10 |
| Project Structure | 5 |
| Package Scripts | 5 |

## التصنيفات

| الدرجة | التصنيف |
|---|---|
| 90-100 | Excellent |
| 75-89 | Good |
| 60-74 | Fair |
| 40-59 | Weak |
| 0-39 | Critical |

## ملفات مهمة

- [INSTALLATION.md](INSTALLATION.md): شرح التثبيت.
- [USAGE.md](USAGE.md): شرح الاوامر والخيارات.
- [REQUIREMENTS.md](REQUIREMENTS.md): المتطلبات.
- [docs/checks.md](docs/checks.md): تفاصيل الفحوصات.
- [docs/roadmap.md](docs/roadmap.md): خارطة الطريق.
- [ARCHITECTURE.md](ARCHITECTURE.md): بنية المشروع.
- [CONTRIBUTING.md](CONTRIBUTING.md): طريقة المساهمة.
- [SECURITY.md](SECURITY.md): سياسة الامان.
- [LICENSE](LICENSE): ترخيص MIT.
