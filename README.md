# بيئة التعلم والتطوير الهندسي لمطور Microsoft Power Platform & Dataverse
## Personal Power Platform Developer Learning Workspace (.NET / C# Track & AB-400 Preparation)

مستودع هندسي شخصي وتطبيقي مصمم لتحويل مطور خبير في تقنيات **.NET / C#** إلى مطور محترف وخبير حلول معتمد في **Microsoft Power Platform & Dataverse**، قادر على بناء حلول مؤسسية متكاملة، واجتياز اختبار الشهادة الدولية **Microsoft AB-400 (Course AB-400T00)**، والتفوق في المقابلات الفنية.

---

## 1. التوجه الاستراتيجي النهائي (Final Project Direction)

**القرار الاستراتيجي الحاسم والنهائي للمشروع**:
تم إنهاء وأرشفة مسار الترجمة وإنتاج الكتب والموسوعات بالكامل، وتحويل المستودع إلى **بيئة تعلم وهندسة برمجية عملية (Hands-On Engineering Learning Environment)** ترتكز على:
1. **التعلم الهندسي القائم على التطبيق**: ربط مفاهيم Dataverse مباشرة بمعمارية .NET المألوفة (مثل: C# Plug-ins مقابل ASP.NET Core Middleware و EF Core Interceptors، Dataverse Web API مقابل OData Controllers، و PCF Controls مقابل React/Blazor Components).
2. **بناء مشروع محفظة أعمال مؤسسي (Enterprise Portfolio)**: نظام متكامل لإدارة دورة حياة الأجهزة والمعدات المؤسسية (`Equipment Provisioning & Asset Lifecycle Management System`) يشمل نماذج البيانات، إضافات C#، خدمات خلفية .NET 8، تكاملات Azure السحابية، ومكونات PCF المتقدمة.
3. **معامل عملية موجهة وتجارب حية**: 9 معامل تطبيقية شاملة تعتمد على الكود المرجعي الرسمي لشركة مايكروسوفت (274 ملف كود محفوظ محلياً).
4. **تتبع تغطية شهادة AB-400**: مصفوفة كفاءات ونظام تتبع تفاعلي مرتبط بدليل دراسة اختبار AB-400 المحدث في 30 أكتوبر 2026.
5. **الاستعداد للمقابلات الوظيفية وسوق العمل**: محاكاة سيناريوهات حقيقية، اختبارات معمارية، وسجلات قرارات هندسية (ADRs).

---

## 2. بنية بيئة العمل النشطة والمؤرشفة (Workspace Structure)

### أ. مساحات العمل النشطة (Active Engineering Workspaces):
```text
e:\Microsoft Dynamics/
├── learning/                          # بيئة التعلم وسجلات المتابعة والأسلوب
│   ├── arabic-style-guide.md          # معايير الصياغة التقنية وأسلوب المهندسين
│   ├── glossary.md                    # المعجم التقني الموجه للمطورين
│   ├── progress.json                  # السجل الآلي لمتابعة إنجاز الكفاءات (5 مستويات)
│   ├── study-log.md                   # سجل الأنشطة المعملية اليومية والأسبوعية
│   └── review-queue.md                # طابور المراجعة والتكرار المتباعد
│
├── labs/                              # المعامل التطبيقية الموجهة
│   ├── 00-environment-setup/          # إعداد البيئة وتثبيت PAC CLI
│   ├── 01-dataverse-foundations/      # نمذجة الجداول والعلاقات والمفاتيح البديلة
│   ├── 02-csharp-plugins/             # إضافات C# المتقدمة والتحكم في دورة المعاملة
│   ├── 03-webapi-client/              # Dataverse Web API و .NET 8 ServiceClient
│   ├── 04-azure-integrations/         # Azure Functions و Service Bus و Webhooks
│   ├── 05-client-scripting/           # برمجة العميل بـ TypeScript و FormContext
│   ├── 06-pcf-controls/               # مكونات PCF باستخدام React و Fluent UI
│   └── 07-automation-copilot/         # الأتمتة المتقدمة و Copilot Studio و MCP
│
├── portfolio/                         # مشروع المحفظة المؤسسي الشامل
│   └── equipment-provisioning/        # نظام إدارة دورة حياة الأجهزة
│       ├── architecture/              # المخططات المعمارية وحدود التنفيذ
│       ├── data-model/                # نموذج البيانات والمفاتيح البديلة
│       ├── dataverse/                 # حلول Dataverse المصدرة والمفككة
│       ├── plugins/                   # مشاريع C# Plug-in واختبارات FakeXrmEasy
│       ├── dotnet/                    # خدمات المزامنة .NET 8 Worker Service
│       ├── power-platform/            # مكونات PCF بـ React وسكربتات TypeScript
│       ├── automation/                # تدفقات العمل ووكلاء Copilot Studio
│       ├── tests/                     # اختبارات التكامل والنشر المستمر
│       └── technical-decisions/       # سجلات القرارات المعمارية (ADRs)
│
├── assessments/                       # التقييمات ومحاكاة المقابلات والاختبارات
│   ├── topic-checkpoints/             # نقاط التحقق المرحلية
│   ├── practical-challenges/          # التحديات الهندسية البرمجية
│   ├── ab400-practice/                # بنك أسئلة سيناريوهات AB-400
│   └── interview-preparation/         # أسئلة مقابلات كبار المطورين
│
├── references/                        # توثيق المصادر الرسمية وحفظ الأصول
│   ├── microsoft-learn.md             # فهرس المسارات الرسمية لكورس AB-400T00
│   ├── github-labs.md                 # فهرس المعامل الرسمية والكود المرجعي
│   └── source-history.json            # سجل التحقق الآلي من المصادر
│
├── roadmap/                           # خارطة الطريق الهندسية ومصفوفة الكفاءات
│   ├── career-goal.md                 # تحديد الهدف المهني وأركان الجدارة
│   ├── learning-roadmap.md            # مسار التعلم المفصل لـ 18 أسبوعاً
│   ├── weekly-plan.md                 # خطة العمل الأسبوعية وقوائم المهام
│   ├── competency-matrix.md           # مصفوفة التقييم ومستويات الإتقان الخمسة
│   └── ab400-objectives.md            # متتبع أهداف اختبار AB-400 (تحديث 2026-10-30)
│
└── reports/                           # تقارير الهجرة والتدقيق اللغوي
    ├── migration-audit.md             # تقرير تدقيق خطة التحول الشاملة
    ├── translation-issues.json        # السجل الآلي لتصنيف مشكلات الترجمة السابقة
    └── translation-quality-report.md  # تقرير المقارنات العملية ونماذج التصحيح
```

### ب. أرشيف الموسوعة التاريخي (READ-ONLY Archive):
```text
archive/legacy-encyclopedia/           # أرشيف مشروع الموسوعة التقنية السابقة (للقراءة فقط)
├── README.md                          # توثيق أسباب الأرشفة والتشغيل وجودة الترجمة
├── book/                              # أصول الموسوعة المحفوظة بالكامل
│   ├── original/                      # النصوص الإنجليزية الأصلية الرسمية (15 ملفاً)
│   ├── translated/                    # النصوص المترجمة والمدققة (الوحدات التجريبية الـ 4)
│   ├── labs-code/                     # 274 ملف شيفرة مرجعية لمعامل مايكروسوفت
│   ├── assets/                        # الصور والمخططات التوضيحية الرسمية
│   ├── config/                        # ملفات إعداد المصادر والمعجم التقني
│   ├── manifests/                     # مانيفست الوحدات وتقارير الاختبارات
│   ├── tools/                         # أدوات بايثون القياسية (validate, build, crawl)
│   ├── pilot-preview.html             # كتاب المعاينة بصيغة HTML (129 ك.ب)
│   └── pilot-preview.pdf              # كتاب المعاينة بصيغة PDF (1.49 م.ب، 26 صفحة)
├── pilot-builds/                      # لقطات المعاينات التجريبية التاريخية
└── translated-v3-snapshot/            # لقطة الوحدات قبل التدقيق اللغوي الأخير
```

---

## 3. إرشادات التشغيل والأدوات (CLI Runbook)

### أوامر مسار التطوير والتعلم (Power Platform CLI):
```powershell
# التحقق من حالة الاتصال ببيئة Dataverse السحابية
pac auth list

# تصدير حل المحفظة المؤسسي كحل غير مدار
pac solution export --name "EquipmentProvisioning" --path "EquipmentProvisioning.zip"

# تفكيك ملف الحل إلى ملفات مصدرية XML داخل Git
pac solution unpack --zipfile "EquipmentProvisioning.zip" --folder "portfolio/equipment-provisioning/dataverse/src"
```

### أوامر تشغيل وفحص الأرشيف التاريخي (Python 3.12 Standard Library Only):
```powershell
# تشغيل فحص التحقق من صحة الوحدات التجريبية الـ 15:
python -X utf8 "archive/legacy-encyclopedia/book/tools/validate.py" --pilot

# تشغيل حزمة اختبارات معايير القبول الـ 18:
python -X utf8 "archive/legacy-encyclopedia/book/tools/test_pipeline.py"

# إعادة توليد وتجميع كتاب المعاينة التجريبي (HTML و PDF):
python -X utf8 "archive/legacy-encyclopedia/book/tools/build.py" --pilot
```
