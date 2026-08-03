# RepoPulse

RepoPulse أداة سطر أوامر بلغة Python تفحص مستودعات GitHub (أو مجلدًا محليًا) وتنتج تقرير صحة بدرجة من 100 مع توصيات عملية.

## أسماء مهمة

| الدور | الاسم الصحيح |
|---|---|
| التثبيت من PyPI | `repopulse-cli` |
| أمر الطرفية | `repopulse` |

**لا تستخدم** `pip install repopulse` — تلك حزمة **أخرى** على الفهرس.

## التثبيت (للمستخدمين)

```bash
pip install repopulse-cli
repopulse --help
```

التحديث:

```bash
pip install -U repopulse-cli
```

من المصدر (للمساهمين):

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
pip install -e ".[dev]"
```

التفاصيل: [INSTALLATION.md](INSTALLATION.md).

## الاستخدام السريع

```bash
# مجلد محلي (بدون شبكة)
repopulse scan .

# مستودع GitHub
repopulse scan https://github.com/username/repository

# فرع أو وسم بدون استنساخ
repopulse scan https://github.com/username/repository/tree/main
repopulse scan https://github.com/username/repository --ref v1.0.0

# مقارنة مرجعين
repopulse compare \
  https://github.com/owner/repo/tree/main \
  https://github.com/owner/repo/tree/feature/x

# معاينة Issues (آمن)
repopulse create-issues https://github.com/owner/repo --dry-run

# بوابة CI
repopulse scan . --fail-under 75 --format summary --quiet
```

الدليل الكامل: [USAGE.md](USAGE.md) (بالإنجليزية).

## الميزات الحالية

- فحص GitHub والملفات المحلية
- مرجع محدد (فرع/وسم) عبر الرابط أو `--ref`
- مقارنة مسحين: `compare` مع `--fail-on-regression`
- إنشاء Issues: `create-issues` (`--dry-run` / `--yes`)
- صيغ: جدول، ملخص، Markdown، JSON، issues
- إعدادات `.repopulse.yml` وملفات تعريف: `strict` · `library` · `docs` · `release`
- كشف أسماء ملفات حساسة دون طباعة المحتوى

## نظام التقييم (افتراضي)

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

| الدرجة | التصنيف |
|---|---|
| 90-100 | Excellent |
| 75-89 | Good |
| 60-74 | Fair |
| 40-59 | Weak |
| 0-39 | Critical |

## ملفات مهمة

- [INSTALLATION.md](INSTALLATION.md) — التثبيت
- [USAGE.md](USAGE.md) — الأوامر والخيارات
- [docs/checks.md](docs/checks.md) — تفاصيل الفحوصات
- [docs/roadmap.md](docs/roadmap.md) — خارطة الطريق
- [CHANGELOG.md](CHANGELOG.md) — سجل الإصدارات
- [README.md](README.md) — الدليل الإنجليزي الكامل

## الترخيص

MIT — انظر [LICENSE](LICENSE).
