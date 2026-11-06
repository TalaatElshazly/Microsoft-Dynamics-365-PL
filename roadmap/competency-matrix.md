# مصفوفة الكفاءة الهندسية ومعايير الاعتماد البرمجي
## Engineering Competency Matrix & Validation Framework

تحدد هذه المصفوفة مستويات الكفاءة الهندسية المعتمدة لمطور **Microsoft Power Platform & Dataverse** المنطلق من خلفية **.NET / C#**، وتحدد شروط الانتقال بين حالات الإتقان وصولاً إلى الاعتماد الفعلي (`VALIDATED`).

---

## 1. حالات الكفاءة الهندسية الخمس (Competency Lifecycle States)

1. **لم تبدأ (`NOT_STARTED`)**:
   - الموضوع مجدول ضمن الخطة ولم تبدأ أية دراسة نظرية أو تطبيقية حوله.
2. **معرفة نظرية واستيعاب معماري (`THEORETICAL`)**:
   - استيعاب المفاهيم الهندسية، وفهم أسباب توفير مايكروسوفت لها، ومقارنتها بمعمارية .NET/C# المألوفة (مثل مقارنة Plug-in بـ ASP.NET Middleware أو EF Core Interceptors).
3. **ممارسة موجهة بالأدلة (`PRACTICED_WITH_GUIDANCE`)**:
   - إكمال المعمل الموجه بنجاح بالاعتماد على التوجيهات التفصيلية أو الشيفرات المرجعية الرسمية.
4. **كفاءة تطبيقية مستقلة (`INDEPENDENT`)**:
   - القدرة على حل مشكلات واقعية وتحديات معملية غير نمطية وتطوير المتطلبات بمفردك دون الحاجة لمتابعة خطوات خطوة بخطوة.
5. **كفاءة معتمدة بالأدلة القطعية (`VALIDATED`)**:
   - **قاعدة صارمة**: لا تُعتمد أية كفاءة كـ `VALIDATED` إلا بوجود أدلة فنية قابلة للفحص:
     - *شيفرة برمجية عاملة وموثقة* (`Working Production Code`).
     - *اختبارات آلية ناجحة* (`Passing Automated Tests` بـ FakeXrmEasy / xUnit).
     - *تحدٍ عملي مكتمل ومجتاز* (`Completed Practical Challenge`).
     - *سجل قرار معماري مبرر ومثبت* (`Approved Architectural Decision Record - ADR`).

---

## 2. جدول الكفاءات التفصيلي ومؤشرات التحقق (Competencies & Verification Evidence)

| معرف الكفاءة (ID) | المهارة / الموضوع المعماري | المقابل في معمارية .NET | الحالة الحالية | الدليل الهندسي المطلوب للاعتماد (Validation Gate) |
|---|---|---|:---:|---|
| **DEV-01-TOOLING** | Power Platform CLI (PAC CLI) وحزم الحلول | dotnet CLI, NuGet packaging | **PRACTICED_WITH_GUIDANCE** | إعداد البيئة وإنشاء ملف مصادقة نشط وتهيئة حل عبر سطر الأوامر |
| **DV-01-SCHEMA** | نمذجة الجداول والعلاقات والمفاتيح البديلة | SQL Tables, EF Core Navigation | **THEORETICAL** | نشر الجداول والمفاتيح البديلة وإثبات Upsert عبر Web API دون GUIDs |
| **DV-02-SECURITY** | وحدات الأعمال، أدوار الأمان، وأمان الحقول | Claims-based RBAC, Row Security | **NOT_STARTED** | اختبار وصول مستخدمين بأدوار مختلفة والتحقق من قيود الصلاحيات |
| **DV-03-BUSINESS-LOGIC** | قواعد العمل وأعمدة الحساب والتجميع والصيغ | FluentValidation, Computed Columns | **NOT_STARTED** | تطبيق قاعدة عمل على نطاق الكيان (Entity Scope) وفحصها برمجياً |
| **DEV-02-ALM-SOLUTIONS** | إدارة الحلول وتفكيكها وحل التبعيات | Assembly dependencies, Artifacts | **NOT_STARTED** | تفكيك الحل عبر `pac solution unpack` وتتبعه كاملاً داخل Git |
| **CODE-01-PLUGIN-ARCH** | دورة حياة الـ Plug-in ومراحل خط الأنابيب (10, 20, 40) | ASP.NET Middleware, EF Interceptors | **THEORETICAL** | كتابة إضافة C# متزامنة في Pre-operation واختبارها عبر FakeXrmEasy |
| **CODE-02-PLUGIN-IMAGES** | صور الكيانات (Pre/Post Images) وتجنب الحلقات | EF OriginalValues vs CurrentValues | **NOT_STARTED** | قراءة قيم الحقول السابقة ومقارنتها ومنع الحلقات عبر `Depth` |
| **CODE-03-PLUGIN-REG** | أداة التسجيل PRT وسمات التصفية والإعدادات الآمنة | DI registration, IOptions pattern | **NOT_STARTED** | تسجيل خطوة وتمرير Secure Config واسترجاعه بنجاح داخل الكود |
| **CODE-04-CUSTOM-APIS** | الواجهات البرمجية المخصصة (Custom APIs) | Custom Controller RPC Endpoints | **NOT_STARTED** | إنشاء Custom API واستدعاؤها كحدث أعمال من C# و Power Automate |
| **INT-01-WEBAPI** | Dataverse Web API (OData v4) والتزامن بـ ETags | ASP.NET Core OData, Optimistic Lock | **NOT_STARTED** | استدعاء مجمع `$batch` مع ترويسة `If-Match` ومنع التعديل المتزامن |
| **INT-02-SERVICECLIENT** | مكتبة .NET 8 ServiceClient والربط المبكر والمتأخر | HttpClient, strongly-typed DbContext | **NOT_STARTED** | تطبيق خدمة كونسول .NET 8 تستخدم الربط المبكر مع سياسة إعادة المحاولة |
| **INT-03-AZURE-FUNCTIONS** | دمج Dataverse مع Azure Functions (C# Isolated) | Serverless Microservices | **NOT_STARTED** | تشغيل دالة Function عبر Webhook وتحديث حالة السجل في Dataverse |
| **INT-04-AZURE-SERVICEBUS** | فك الترابط عبر Azure Service Bus و Event Grid | Message Brokers, MassTransit | **NOT_STARTED** | نشر أحداث Dataverse إلى طابور Service Bus واستهلاكها بنجاح |
| **UX-01-CLIENTSCRIPT** | برمجة العميل بـ TypeScript و FormContext | Angular / React client validation | **NOT_STARTED** | كتابة سكربت TypeScript مع ترجمة Webpack والتحكم في حقول النموذج |
| **UX-02-PCF-REACT** | مكونات PCF التفاعلية عبر React و Fluent UI | Custom Web / Blazor Components | **NOT_STARTED** | بناء مكون PCF لاختيار الأجهزة بصرياً ونشره داخل نموذج Dataverse |
| **APP-01-MODEL-DRIVEN** | التطبيقات المبنية على نموذج والصفحات المخصصة | Admin UI Portals, UI Shells | **NOT_STARTED** | بناء تطبيق Model-driven متكامل يربط عمليات تخصيص المعدات |
| **APP-02-CANVAS-EXT** | تطبيقات اللوحة و Power Fx المتقدم والتفويض | Declarative UI, In-memory LINQ | **NOT_STARTED** | بناء شاشة طلب سريعة مع استعلامات قابلة للتفويض ومجموعات بيانات |
| **APP-03-CODE-APPS** | تطبيقات الشيفرة البرمجية (Code Apps) | Modern Single Page Apps (SPA) | **NOT_STARTED** | بناء تطبيق واجهة أمامية حديث يتصل مباشرة بـ Dataverse SDK |
| **AUTO-01-CLOUD-FLOWS** | مسارات Power Automate والتزامن ومعالجة الأخطاء | Background Workers, Workflow Core | **NOT_STARTED** | مسار تدفق يرسل بطاقة اعتماد تفاعلية في Teams ويعالج الفشل تلقائياً |
| **AUTO-02-CUSTOM-CONNECTORS** | الموصلات المخصصة وتعريفات OpenAPI و OAuth2 | Refit / Generated API Clients | **NOT_STARTED** | بناء موصل مخصص لنظام صيانة خارجي وتأمينه بتوكن Bearer |
| **AI-01-COPILOT-STUDIO** | وكلاء Copilot Studio والإجراءات التوليدية | Semantic Kernel, LLM Orchestrations | **NOT_STARTED** | إعداد وكيل ذكي يجيب على أسئلة حالة العهدة ويطلق إجراءات معتمدة |
| **AI-02-MCP-AGENTS** | تكامل بروتوكول سياق النموذج (MCP) في Power Platform | Standardized Agent Tool Servers | **NOT_STARTED** | ربط خادم MCP خارجي ببيئة Dataverse للاستعلام الآلي بالأدوات |
| **TEST-01-AUTOMATED-TESTING** | اختبارات الوحدة بـ FakeXrmEasy وفحص الحلول | xUnit, Moq, InMemory EF Core DB | **NOT_STARTED** | حزمة اختبارات وحدة تغطي كافة حالات فشل ونجاح إضافات C# في CI |
| **ALM-01-AZDO-GHA** | أتمتة النشر المستمر بـ GitHub Actions / DevOps | CI/CD YAML Pipelines, Release Gates | **NOT_STARTED** | مسار CI/CD مؤتمت يبني ويفحص الحل وينشره كحل مدار (Managed) |
