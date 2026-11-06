# مسرد المصطلحات المعمارية لمطور Power Platform & Dataverse (Technical Glossary)

يحدد هذا المسرد سياسة التعامل مع المصطلحات التقنية في كافة الشروحات والمذكرات والمعامل داخل مساحة العمل، مع مراعاة المقارنة الهندسية لمطوري .NET / C#.

---

## 1. مصطلحات أساسية تبقى بالإنجليزية دوماً (Strict English Technical Terms)

| المصطلح التقني | المعنى والدور المعماري في Dataverse | المقابل التقريبي في عالم .NET / C# |
| :--- | :--- | :--- |
| **Microsoft Dataverse** | قاعدة البيانات الذكية ومنصة البيانات المؤسسية السحابية من مايكروسوفت. | Relational Database + Auto-generated OData REST API + Built-in Security & Audit. |
| **Plug-in** | صنف C# ينفذ `IPlugin` يعمل على جانب الخادم استجابة لأحداث البيانات. | EF Core Interceptor / MediatR Pipeline Behavior / Database Trigger on steroids. |
| **Execution Pipeline** | خط أنابيب معالجة الرسائل متعدد المراحل (PreValidation, PreOperation, MainOperation, PostOperation). | ASP.NET Core Middleware Pipeline / HTTP Message Handlers. |
| **IPluginExecutionContext** | واجهة توفر كافة بيانات وسياق العملية الجارية (Target, Pre/Post Images, SharedVariables, Depth). | `HttpContext` / `ActionExecutingContext` في ASP.NET Core. |
| **IOrganizationService** | واجهة SDK الرئيسية لتنفيذ عمليات CRUD والاستعلامات واستدعاء الرسائل على Dataverse. | `DbContext` في EF Core / Service Gateway. |
| **Custom API** | رسالة مخصصة مسماة يحددها المطور بمعاملات دخل وخرج وتُنفذ عبر Plug-in. | Custom API Controller Endpoint / CQRS Command Handler. |
| **Power Apps Component Framework (PCF)** | إطار عمل لبناء مكونات واجهة مستخدم مخصصة باستخدام TypeScript و React. | Custom Angular / React Web Component or Razor Component. |
| **Managed / Unmanaged Solutions** | حزم توزيع المكونات وإدارة دورة حياة التطبيقات (ALM). | NuGet Package vs Source Code Project / Assembly References. |
| **Plugin Registration Tool (PRT)** | أداة سطح مكتب لتسجيل تجميعات الـ Plug-in والخطوات والصور ونقاط النهاية. | Dependency Injection / Middleware Registration tool. |
| **Pre-image / Post-image** | لقطة لحالة السجل قبل بدء المعاملة أو بعد اكتمالها في قاعدة البيانات. | EF Core `ChangeTracker.OriginalValues` vs `CurrentValues`. |
| **Filtering Attributes** | قائمة الأعمدة المحددة التي يُشترط تعديلها لإطلاق تشغيل الخطوة. | Column-level Trigger Condition / Field Dirty Tracking. |
| **Model Context Protocol (MCP)** | بروتوكول قياسي مفتوح لربط وكلاء الذكاء الاصطناعي بمصادر البيانات والأدوات. | AI Agent Tool Provider / API Connector for LLMs. |

---

## 2. مصطلحات سياقية تُعرّب بأسلوب فني سليم (Contextual Terms)

| المصطلح | الترجمة الفنية المعتمدة | الاستخدام والسياق |
| :--- | :--- | :--- |
| **Trigger** | مُحفّز / مشغّل الحدث | الإشارة أو الحدث البرمجي الذي يبدأ تشغيل كود معين (وليس "ما يطلق شرارة"). |
| **Runtime** | بيئة تشغيل / بيئة تنفيذ | المنصة أو الحاوية التي ينفذ الكود بداخلها (وليس "موطن فيزيائي"). |
| **Stateless** | عديم الحالة | عدم احتفاظ الصنف ببيانات طلبات محددة بين الاستدعاءات المتتالية في الذاكرة. |
| **Depth** | عمق التنفيذ | مؤشر عدد مرات استدعاء الـ Plug-in لنفسه أو لخطوات متتالية في مكدس العمليات. |
| **Re-entry** | إعادة الدخول | تسبب الـ Plug-in في إطلاق نفسه مجدداً مما قد يسبب حلقات مفرغة (Infinite Loops). |
| **Alternate Key** | مفتاح بديل | عمود أو مجموعة أعمدة تمثل معرّفاً فريداً لسجل غير المعرّف الأساسي (GUID). |
| **Upsert** | تحديث أو إدراج (Upsert) | عملية فحص ذكية تقوم بالتعديل إن وجد السجل أو الإنشاء إن لم يكن موجوداً. |
| **Change Tracking** | تتبع التغييرات | ميزة في Dataverse تتيح للأنظمة الخارجية استرجاع السجلات المعدلة فقط دلتا (Delta). |
