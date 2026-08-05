# RepoPulse

[![CI](https://github.com/3ssiri/RepoPulse/actions/workflows/ci.yml/badge.svg)](https://github.com/3ssiri/RepoPulse/actions/workflows/ci.yml)
[![CodeQL](https://github.com/3ssiri/RepoPulse/actions/workflows/codeql.yml/badge.svg)](https://github.com/3ssiri/RepoPulse/actions/workflows/codeql.yml)
[![PyPI version](https://img.shields.io/pypi/v/repopulse-cli.svg)](https://pypi.org/project/repopulse-cli/)
[![Python](https://img.shields.io/pypi/pyversions/repopulse-cli.svg)](https://pypi.org/project/repopulse-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

```bash
pip install repopulse-cli
repopulse scan .
```

**RepoPulse** أداة سطر أوامر بلغة بايثون تفحص مستودعات GitHub (أو مجلدًا محليًا) وتنتج **تقرير صحة** عمليًا: درجة من 100، فحوصات ناجح/تحذير/فشل، وتوصيات قابلة للتنفيذ.

موجّهة للمطوّرين الذين يريدون مراجعة سريعة من الطرفية، وللمحافظين الذين يحتاجون أداة خفيفة في CI أو قبل الإصدار أو عند فرز المهام.

| الدور | الاسم الصحيح |
|---|---|
| التثبيت من الفهرس | `repopulse-cli` |
| أمر الطرفية | `repopulse` |
| الاستيراد في بايثون | `repopulse` |

> **مهم:** لا تشغّل `pip install repopulse` — تلك حزمة **أخرى** على الفهرس وغير مرتبطة بهذا المشروع. استخدم دائمًا **`repopulse-cli`**.

## التثبيت (للمستخدمين)

```bash
pip install repopulse-cli
repopulse --help
```

التحديث:

```bash
pip install -U repopulse-cli
```

بيئة معزولة (مُستحسنة إن تعارضت إصدارات المكتبات مع أدوات أخرى):

```bash
python -m venv .venv
# ويندوز PowerShell:
.\.venv\Scripts\Activate.ps1
# ماك / لينكس:
# source .venv/bin/activate
pip install repopulse-cli
```

من عجلة إصدار GitHub (إن فضّلت عدم استخدام الفهرس):

```bash
pip install https://github.com/3ssiri/RepoPulse/releases/download/v0.3.5/repopulse_cli-0.3.5-py3-none-any.whl
```

التفاصيل الكاملة: [INSTALLATION.md](INSTALLATION.md) (بالإنجليزية).

## البداية السريعة

```bash
# مجلد محلي (بدون شبكة / بدون واجهة GitHub)
repopulse scan .

# مستودع عام
repopulse scan https://github.com/psf/requests

# فرع أو وسم محدد (بدون استنساخ كامل)
repopulse scan https://github.com/psf/requests/tree/main
repopulse scan https://github.com/psf/requests --ref v2.32.0

# بوابة CI (يفشل إن انخفضت الدرجة عن العتبة)
repopulse scan https://github.com/username/repository --fail-under 75 --format summary --quiet

# مقارنة مرجعين أو مجلدين
repopulse compare \
  https://github.com/owner/repo/tree/main \
  https://github.com/owner/repo/tree/feature/pr-42 \
  --fail-on-regression

# معاينة Issues (آمن — لا ينشئ شيئًا)
repopulse create-issues https://github.com/owner/repo --dry-run
```

المستودعات الخاصة: مرّر `--token` أو عيّن:

```bash
GITHUB_TOKEN
```

التفاصيل: [USAGE.md](USAGE.md).

## الميزات (الإصدار الحالي)

### الفحص

- فحص مستودعات **GitHub العامة** عبر الرابط.
- فحص **مجلد محلي** دون شبكة: `repopulse scan .`
- فحص **فرع / وسم / commit** عبر الرابط (`/tree/<ref>` أو `/releases/tag/<tag>`) أو `--ref`
- مستودعات **خاصة** مع التوكن
- نفس مسار الفحوصات للمصدر المحلي والبعيد

### التقارير والمخرجات

- درجة من **100** مع تصنيفات (ممتاز → حرج)
- جدول طرفية غني (الافتراضي)
- الصيغ: `table` · `summary` · `markdown` · `json` · `issues`
- تصدير Markdown (`--export`) وكتابة أي صيغة إلى ملف (`--output`)
- عقد JSON ثابت (`schema_version` 1.0) — انظر [docs/json-schema.md](docs/json-schema.md)
- Markdown أغنى: عدّادات pass/warn/fail وقسم الانتباه

### المقارنة

```text
repopulse compare <baseline> <target>
```

- مسارات محلية و/أو روابط GitHub
- مراجع لكل طرف: روابط `tree` أو `--baseline-ref` / `--target-ref`
- صيغ: جدول، markdown، json، summary
- بوابة CI: `--fail-on-regression` (رمز خروج `2` عند التراجع)

### Issues والأتمتة

- `--format issues` — نص جاهز للصق في Issues
- `repopulse create-issues` — إنشاء Issues حقيقية (`--dry-run` أو `--yes`)
  - **منع التكرار افتراضيًا** (يتخطى العناوين المطابقة لـ Issues مفتوحة)
  - `--no-dedupe` لإجبار الإنشاء
- مثال CI: [examples/github-action-repopulse.yml](examples/github-action-repopulse.yml)
- إعدادات اختيارية `.repopulse.yml` وملفات تعريف:

```text
strict · library · docs · release
```

### الأمان

- كشف **أسماء** ملفات حساسة (مثل `.env` والمفاتيح) **دون** طباعة المحتوى
  - تحت `tests/` أو `examples/`: تحذير (غالباً fixtures)
  - في جذر المشروع أو الكود الإنتاجي: فشل
- فحوصات استشارية للتبعيات والأساس الأمني (توصيات دون تغيير الدرجة المئوية افتراضيًا)

## الأوامر

| الأمر | الغرض |
|---|---|
| `repopulse scan <url-or-path>` | تقرير صحة لمستودع أو مجلد واحد |
| `repopulse compare <baseline> <target>` | فرق بين تقريرين |
| `repopulse create-issues <url-or-path>` | إنشاء Issues من فحوصات fail/warn |

## الإعداد

يُقرأ `.repopulse.yml` من المجلد الحالي إن وُجد، أو عبر `--config`:

```bash
repopulse scan . --config examples/repopulse.yml
```

```yaml
profile: release   # اختياري: strict | library | docs | release
fail_under: 90
disabled_checks:
  - activity
weights:
  tests: 25
  github_actions: 20
```

ملفات جاهزة: [examples/profiles/](examples/profiles/).

## نظام التقييم (الأوزان الافتراضية)

| الفحص | النقاط |
|---|---:|
| جودة README | 20 |
| الترخيص | 10 |
| ملف التجاهل | 10 |
| الاختبارات | 15 |
| GitHub Actions | 15 |
| النشاط الأخير | 10 |
| ملفات حساسة | 10 |
| بنية المشروع | 5 |
| سكربتات الحزمة | 5 |

| الدرجة | التصنيف |
|---|---|
| 90–100 | Excellent (ممتاز) |
| 75–89 | Good (جيد) |
| 60–74 | Fair (مقبول) |
| 40–59 | Weak (ضعيف) |
| 0–39 | Critical (حرج) |

فحوصات التبعيات والأساس الأمني **استشارية**: تضيف توصيات دون تغيير المجموع المسجّل.

مرجع الفحوصات: [docs/checks.md](docs/checks.md).

### ملاحظات من التجربة على مستودعات حقيقية

بعد تحسينات الفحوصات الأخيرة، أمثلة تقريبية (تتغيّر مع الوقت):

| المستودع | الدرجة (تقريبي) |
|---|---:|
| هذا المشروع | ~100 |
| مشاريع بايثون ناضجة (مثل requests / Flask) | غالبًا 90+ |
| أنظمة غير بايثون (مثل Go) | أقل — الاستدلال لا يزال يميل لبايثون/JS |

لقطة أطول: [docs/dogfood.md](docs/dogfood.md).

## مثال مخرجات

```text
RepoPulse Health Report for psf/requests
Score: 91 / 100 - Excellent

Checks
README Quality      PASS   16/20
License             PASS   10/10
.gitignore          PASS   10/10
Tests               WARN   12/15
GitHub Actions      PASS   15/15
```

## التثبيت للمساهمين / من المصدر

```bash
git clone https://github.com/3ssiri/RepoPulse.git
cd RepoPulse
pip install -e ".[dev]"
pytest
ruff check .
```

انظر [CONTRIBUTING.md](CONTRIBUTING.md) و [INSTALLATION.md](INSTALLATION.md).

## الوثائق

| الملف | المحتوى |
|---|---|
| [INSTALLATION.md](INSTALLATION.md) | التثبيت، العجلة، المصدر، التوكن، الأعطال |
| [USAGE.md](USAGE.md) | كل الأوامر والخيارات وCI |
| [REQUIREMENTS.md](REQUIREMENTS.md) | المتطلبات |
| [docs/checks.md](docs/checks.md) | ماذا يفحص كل فحص |
| [docs/json-schema.md](docs/json-schema.md) | عقد JSON |
| [docs/PUBLISHING.md](docs/PUBLISHING.md) | النشر (للمحافظين) |
| [docs/roadmap.md](docs/roadmap.md) | خارطة الطريق |
| [docs/dogfood.md](docs/dogfood.md) | نتائج على مستودعات حقيقية |
| [ARCHITECTURE.md](ARCHITECTURE.md) | بنية الكود |
| [CHANGELOG.md](CHANGELOG.md) | سجل الإصدارات |
| [README.md](README.md) | الدليل الإنجليزي الكامل |
| [README.es-ES.md](README.es-ES.md) | ملخص إسباني |

## المتطلبات

- بايثون **3.11** أو أحدث
- شبكة إلى `api.github.com` للفحوصات البعيدة
- توكن GitHub للمستودعات الخاصة أو حدود أعلى أو `create-issues --yes`

## المساهمة

نرحّب بالمساهمات — خصوصًا **الإبلاغ عن إيجابيات كاذبة** من مستودعات حقيقية، وتحسينات الفحوصات الصغيرة، والوثائق.

عند الإبلاغ عن نتيجة غير عادلة، اذكر إن أمكن:

1. رابط المستودع
2. إصدار الأداة
3. مفتاح الفحص (مثل `license` أو `github_actions`)
4. لماذا النتيجة خاطئة

التفاصيل: [CONTRIBUTING.md](CONTRIBUTING.md).

## الترخيص

MIT — انظر [LICENSE](LICENSE).

## روابط

- الفهرس: https://pypi.org/project/repopulse-cli/
- الإصدارات: https://github.com/3ssiri/RepoPulse/releases
- Issues: https://github.com/3ssiri/RepoPulse/issues
