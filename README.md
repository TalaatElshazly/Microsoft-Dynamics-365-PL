# بيئة التعلم والتطوير الهندسي لمطور Microsoft Power Platform & Dataverse
## Personal Power Platform Developer Learning Workspace (.NET / C# Developer Track & AB-400 Preparation)

مستودع هندسي شخصي متكامل لتحويل مطور **.NET / C#** محترف إلى مطور وخبير حلول **Microsoft Power Platform & Dataverse** معتمد، قادر على بناء حلول مؤسسية متكاملة واجتياز اختبار الشهادة الدولية **Microsoft AB-400 (Course AB-400T00)**.

---

## 1. هوية المشروع والهدف المهني (Mission & Career Objective)

الهدف من هذا المستودع ليس مجرد الترجمة السطحية للوثائق، بل **بناء مهارات برمجية وهندسية عملية حقيقية**:
1. **التعلم الهندسي القائم على التطبيق**: ربط مفاهيم Dataverse مباشرة بمعمارية .NET المألوفة (مثل: Plug-ins مقابل ASP.NET Core Middleware و EF Core Interceptors، Dataverse Web API مقابل OData Controllers، و PCF Controls مقابل React/Blazor Components).
2. **بناء مشروع محفظة أعمال مؤسسي (Enterprise Portfolio)**: نظام متكامل لإدارة دورة حياة الأجهزة والمعدات المؤسسية (`Equipment Provisioning & Asset Lifecycle Management System`) يشمل نماذج البيانات، إضافات C#، خدمات خلفية .NET 8، تكاملات Azure السحابية، ومكونات PCF المتقدمة.
3. **معامل عملية وتجارب حية**: 9 معامل تطبيقية شاملة تعتمد على الكود المرجعي الرسمي لشركة مايكروسوفت (274 ملف كود محفوظ محلياً).
4. **تتبع تغطية شهادة AB-400**: مصفوفة كفاءات ونظام تتبع تفاعلي مرتبط بدليل دراسة اختبار AB-400 المحدث في 30 أكتوبر 2026.
5. **قاعدة معرفية تقنية باللغة العربية الاحترافية**: صياغة دقيقة غير حرفية تراعي المصطلحات البرمجية الإنجليزية الأصلية مع شرح عربي هندسي رصين.

---

## 2. بنية المستودع (Repository Structure)

```text
e:\Microsoft Dynamics/
├── roadmap/                           # خارطة الطريق الهندسية ومصفوفة الكفاءات
│   ├── career-goal.md                 # تحديد الهدف المهني وأركان الجدارة
│   ├── learning-roadmap.md            # مسار التعلم المفصل لـ 18 أسبوعاً
│   ├── weekly-plan.md                 # خطة العمل الأسبوعية وقوائم المهام
│   ├── competency-matrix.md           # مصفوفة التقييم ومستويات الإتقان
│   └── ab400-objectives.md            # متتبع أهداف اختبار AB-400 (تحديث 2026-10-30)
│
├── learning/                          # بيئة التعلم وسجلات المتابعة والأسلوب
│   ├── arabic-style-guide.md          # معايير الصياغة التقنية وأسلوب المهندسين
│   ├── glossary.md                    # المعجم التقني الموجه للمطورين
│   ├── progress.json                  # السجل الآلي لمتابعة إنجاز الكفاءات
│   ├── study-log.md                   # سجل الأنشطة المعملية اليومية والأسبوعية
│   └── review-queue.md                # طابور المراجعة والتكرار المتباعد
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
├── book/                              # الأصول المعرفية المحفوظة محلياً
│   ├── original/                      # النصوص الإنجليزية الرسمية الأصلية
│   ├── translated/                    # النصوص التقنية المترجمة والمدققة لغوياً
│   ├── labs-code/                     # 274 ملف كود مرجعي رسمي لمعامل مايكروسوفت
│   ├── assets/                        # الصور والمخططات التوضيحية
│   └── tools/                         # أدوات سطر الأوامر (الزحف، التحقق، البناء)
│
├── archive/                           # أرشفة خط إنتاج الكتب السابق
│   └── legacy-book-pipeline/          # توثيق ولقطات خط إنتاج الكتب والـ PDF السابق
│
└── reports/                           # تقارير الهجرة والتدقيق اللغوي
    ├── migration-audit.md             # تقرير تدقيق خطة التحول الشاملة
    ├── translation-issues.json        # السجل الآلي لتصنيف مشكلات الترجمة السابقة
    └── translation-quality-report.md  # تقرير المقارنات العملية ونماذج التصحيح
```

---

## 3. إرشادات التشغيل والأدوات (CLI Runbook)

### أدوات مسار التعلم و PAC CLI:
- **عرض حالة المصادقة في Dataverse**:
  `pac auth list`
- **تصدير الحل المؤسسي غير المدار**:
  `pac solution export --name "EquipmentProvisioning" --path "EquipmentProvisioning.zip"`
- **تفكيك الحل إلى ملفات مصدرية داخل Git**:
  `pac solution unpack --zipfile "EquipmentProvisioning.zip" --folder "portfolio/equipment-provisioning/dataverse/src"`

### فحص ومطابقة أدوات المستودع القياسية (Python 3.12 Standard Library Only):
- **فحص التحقق من صحة الوحدات والمصطلحات**:
  `python -X utf8 "book/tools/validate.py" --pilot`
- **بناء المعاينة التجريبية الأرشيفية (HTML و PDF)**:
  `python -X utf8 "book/tools/build.py" --pilot`
