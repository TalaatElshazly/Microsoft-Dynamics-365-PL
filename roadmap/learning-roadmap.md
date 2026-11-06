# الخطة التعليمية الشاملة لـ 18 أسبوعاً (18-Week Developer Roadmap)

**الافتراض الزمني:** 15 إلى 20 ساعة أسبوعياً من الدراسة المتعمقة والعمل البرمجي المخبري.  
**المنهجية:** جسر معرفي ينطلق من مفاهيم .NET / C# المألوفة إلى مفاهيم Dataverse و Power Platform الموازية.

---

## المرحلة 0: تهيئة بيئة المطور وأدوات العمل (Phase 0: Environment Setup)
- **المدة:** 2–3 أيام.
- **المحاور:**
  - التحقق من صلاحيات بيئة Power Apps Developer Plan.
  - تثبيت وضبط Power Platform CLI (`pac`).
  - تهيئة Visual Studio 2022 و VS Code مع حزم تطوير .NET Framework 4.8 و .NET 8+.
  - إعداد مستودع Git وإنشاء أول حل غير مدار (Unmanaged Solution).
- **المخرج العملي:** بيئة تطوير متصلة وجاهزة لتسجيل الإضافات واستدعاء الـ APIs.

---

## المرحلة 1: أساسيات Dataverse ونمذجة البيانات المؤسسية (Phase 1: Dataverse Foundations)
- **المدة:** الأسبوع 1 – 2.
- **المحاور الهندسية لمطور .NET:**
  - مقارنة جداول Dataverse بجداول SQL Server و Entities في EF Core.
  - العلاقات (1:N, N:1, N:N) والقيود المرجعية وسلوك التعاقب (Cascading Behavior).
  - أنواع الأعمدة والخيارات (Choices) والمفاتيح البديلة (Alternate Keys).
  - بناء تطبيق مبني على النموذج (Model-driven App) وتصميم النماذج والعروض.
  - قواعد العمل (Business Rules) كبديل للمنطق البسيط.
  - مصفوفة الأمان: الأدوار (Security Roles)، ووحدات الأعمال (Business Units)، والفرق (Teams)، ومشاركة السجلات.
  - الحلول المدارة وغير المدارة (Managed vs Unmanaged Solutions).
- **المشروع العملي:** بناء هيكل البيانات الكامل لنظام **Equipment Provisioning** وضبط العلاقات والأمان.

---

## المرحلة 2: برمجة إضافات C# Dataverse Plug-ins (Phase 2: Server-Side Logic)
- **المدة:** الأسبوع 3 – 5.
- **المحاور الهندسية لمطور .NET:**
  - خط أنابيب الأحداث (Event Execution Pipeline): الفروق الحاسمة بين PreValidation و PreOperation و PostOperation.
  - تنفيذ واجهة `IPlugin` وتشريح `IServiceProvider` و `IPluginExecutionContext`.
  - معمارية النسخ المخبأة (Caching) والإلزام الصارم بكون الصنف عديم الحالة (Stateless).
  - استخدام الصور القبلية والبعدية (Pre-image & Post-image) بدلاً من استعلامات قاعدة البيانات الزائدة.
  - تسجيل التجميعات والخطوات والصور عبر أداة Plugin Registration Tool ومقارنتها بحقن التبعيات (DI).
  - حدود المعاملات المصرفية (Transactions)، وعمق التنفيذ (Depth)، ومعالجة الاستثناءات `InvalidPluginExecutionException`.
- **المشروع العملي:** بناء وتسجيل واختبار إضافات C# المتقدمة للتحقق من أهلية استبدال الأجهزة في نظام المعرض.

---

## المرحلة 3: واجهات برمجة المنصة وتكاملات .NET المتقدمة (Phase 3: Dataverse APIs & .NET)
- **المدة:** الأسبوع 6 – 7.
- **المحاور الهندسية لمطور .NET:**
  - المقارنة بين Dataverse Web API (OData RESTful) و Organization Service SDK (`ServiceClient`).
  - صياغة استعلامات `QueryExpression` و `FetchXml` ومعادلتها مع LINQ و SQL.
  - المصادقة الحديثة عبر Microsoft Entra ID وتطبيقات الخدمة (Service Principals / App Registrations).
  - عمليات الدفعات المجمعة (`ExecuteMultipleRequest` / `ExecuteTransactionRequest`).
  - معالجة حدود استهلاك الواجهة (API Throttling Limits) وسياسات إعادة المحاولة المرنة (Retry Policies مع Polly).
  - بناء وتوثيق واجهات برمجية مخصصة (Custom APIs) بروابط رسائل وأحداث مخصصة.
- **المشروع العملي:** بناء تطبيق Web API مستقل بلغة ASP.NET Core يتكامل مع Dataverse لإدارة طلبات المعدات.

---

## المرحلة 4: تكاملات السحابة وخدمات Azure (Phase 4: Azure Integrations)
- **المدة:** الأسبوع 8 – 9.
- **المحاور الهندسية لمطور .NET:**
  - معالجة العمليات طويلة الأمد عبر Azure Functions غير المتزامنة.
  - نقاط نهاية خدمة Dataverse: Webhooks، و Azure Service Bus، و Event Hubs.
  - نشر واستهلاك أحداث الأعمال (Dataverse Business Events).
  - مزامنة البيانات عبر تتبع التغييرات (Change Tracking).
  - الهوية المدارة (Managed Identity) والربط الآمن بدون أسرار مضمنة.
  - مراقبة وتتبع العمليات عبر Azure Application Insights.
- **المشروع العملي:** تكامل نظام المعدات مع خدمة جرد خارجية عبر Azure Function و Service Bus.

---

## المرحلة 5: تجربة المستخدم ومكونات PCF (Phase 5: Power Apps & PCF)
- **المدة:** الأسبوع 10 – 12.
- **المحاور الهندسية لمطور .NET و Angular/TypeScript:**
  - برمجة جانب العميل في Model-driven Apps عبر Client API وكائنات `formContext`.
  - تخصيص شريط الأوامر (Command Bar) عبر Power Fx و JavaScript.
  - إطار عمل مكونات Power Apps (PCF): دورة حياة المكون ومخطط البيانات `ControlManifest.Input.xml`.
  - تطوير مكونات PCF تفاعلية باستخدام TypeScript ومكتبة React.
  - تطبيقات الكود (Power Apps Code Apps).
- **المشروع العملي:** بناء مكون PCF تفاعلي لعرض حالة وفحص سلامة الأجهزة (Device Condition Selector).

---

## المرحلة 6: الأتمتة المتقدمة ووكلاء الذكاء الاصطناعي (Phase 6: Automation & AI Agents)
- **المدة:** الأسبوع 13 – 14.
- **المحاور الهندسية لمطور .NET:**
  - مسارات Power Automate السحابية المرنة ومعالجة الأخطاء والتعبيرات المتقدمة.
  - بناء الموصلات المخصصة (Custom Connectors) عبر تعريفات OpenAPI و Azure Functions.
  - بناء وتوجيه وكلاء Copilot Studio وتكاملهم مع Dataverse.
  - تكامل الوكلاء المخصصين عبر بروتوكول سياق النموذج (Model Context Protocol - MCP) ومكتبات Microsoft Foundry.
- **المشروع العملي:** بناء أتمتة اعتماد مؤمنة ووكيل ذكي يستعلم عن أهلية المعدات عبر خادم Dataverse MCP.

---

## المرحلة 7: إدارة دورة حياة التطبيقات والأمان المؤسسي (Phase 7: Security & ALM)
- **المدة:** الأسبوع 15 – 16.
- **المحاور الهندسية لمطور .NET:**
  - إدارة طبقات الحلول (Solution Layers) وفض التعارضات.
  - متغيرات البيئة (Environment Variables) ومراجع الاتصال (Connection References).
  - مسارات نشر Power Platform Pipelines وأدوات البناء CI/CD عبر GitHub Actions و Azure DevOps.
  - حوكمة البيئات وسياسات تفادي فقدان البيانات (Data Loss Prevention - DLP).
- **المشروع العملي:** أتمتة تصدير ونشر حل Equipment Provisioning من بيئة التطوير إلى بيئة الاختبار.

---

## المرحلة 8: المراجعة الشاملة واستعدادات AB-400 والمقابلات (Phase 8: AB-400 & Career Prep)
- **المدة:** الأسبوع 17 – 18.
- **المحاور:**
  - مراجعة تدقيق كافة متطلبات دليل دراسة AB-400 الرسمي المحدث.
  - خوض اختبارات تقييم عملية وتحديات برمجية موقوتة.
  - صقل وتوثيق معرض الأعمال (Portfolio Repository) ومخططاته المعمارية على GitHub.
  - محاكاة المقابلات الفنية لمهندس Power Platform / .NET Developer.
