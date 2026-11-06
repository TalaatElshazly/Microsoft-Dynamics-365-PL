# مصفوفة تدقيق أهداف اختبار Microsoft AB-400 الرسمي (Exam AB-400 Objectives Coverage Tracker)

**مصدر التدقيق الرسمي المباشر:** [Study guide for Exam AB-400 (Updated October 30, 2026)](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ab-400)  
**اسم الاختبار:** Exam AB-400: Extending Microsoft Power Platform Solutions with Code and AI  
**الدورة التدريبية الرسمية:** Course AB-400T00  
**تاريخ التحقق المباشر من واجهة مايكروسوفت:** 2026-11-06  

> [!IMPORTANT]
> **قاعدة التمييز الصارمة بين تغطية المنهج والجاهزية للاختبار**:
> هذا الجدول يوثق مواءمة محتوى المستودع مع الأهداف الرسمية المحدثة لاختبار **AB-400** الصادر في **30 أكتوبر 2026**.
> **لا يجوز الادعاء بجاهزية المطور للاختبار استناداً فقط إلى توثيق المنهج أو مطابقة العناوين**.
> نقسم التتبع بدقة إلى ثلاثة مستويات منفصلة:
> 1. **تغطية المصادر الرسمية (Official Source Coverage)**: توفر الوثائق والمراجع الرسمية من مايكروسوفت (100% متوفرة محلياً ورقمياً).
> 2. **التطبيق العملي الموجه (Guided Practical Coverage)**: توفر وإنجاز المعامل الموجهة والشيفرات المرجعية.
> 3. **الاعتماد البرمجي الفعلي (Actual Competency Validation)**: إثبات المهارة عملياً بشكل مستقل باختبارات آلية وشيفرة عاملة مثبتة في progress.json.

### حالات التتبع المعتمدة في هذا الجدول:
- `SOURCE_AVAILABLE`: المرجع الرسمي منشور ومتوفر بالكامل في بيئة العمل.
- `GUIDED_LAB_AVAILABLE`: الكود المرجعي الرسمي للمعمل محفوظ في archive/legacy-encyclopedia/book/labs-code/.
- `THEORETICAL`: تمت دراسة المفهوم المعماري ومقارنته بمنظومة .NET/C#.
- `PRACTICED_WITH_GUIDANCE`: تم تنفيذ المعمل الموجه بالكامل على البيئة السحابية.
- `INDEPENDENT`: تم إنجاز حلول وتحديات مستقلة بنجاح دون الرجوع للأدلة.
- `VALIDATED`: كفاءة معتمدة قطيعاً بأدلة فنية قابلة للاختبار والفحص (شيفرة + اختبارات xUnit/FakeXrmEasy).
- `GAP`: موضوع مجدول لم يتم البدء في دراسته بعد.

---

## المجال 1: بناء حلول Microsoft Power Platform المتقدمة (15–20%)

### 1.1 تصميم المعمارية الفنية (Design the technical architecture)
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| تحليل المعمارية الفنية لتحديد مكونات الحل وأسلوب تنفيذها | `learn.wwl.design-power-platform-architectures` | مصفوفة بيئات التشغيل الخمس في `labs/01/` | `COVERED_THEORETICALLY` |
| تصميم المصادقة والتفويض لمكونات الحل (AuthN & AuthZ) | `learn.wwl.design-power-platform-architectures` | تهيئة Service Principal في Entra ID | `GAP` |
| تحديد متى تُلبى المتطلبات عبر الميزات الجاهزة (OOB vs Custom) | `learn.wwl.get-started-power-platform-development` | مقارنة Business Rules مقابل C# Plugins | `PRACTICED` |
| تحديد موضع تنفيذ منطق الأعمال (سحابي، عميل، خادم، أتمتة) | `learn.wwl.get-started-power-platform-development` | تمرين حماية قاعدة استحقاق الأجهزة على الخادم | `VALIDATED` |
| تحديد متى تُستخدم الجداول القياسية أو الظاهرية أو المرنة | `learn.wwl.design-power-platform-architectures` | نمذجة كيانات Equipment Provisioning | `PRACTICED` |
| تقييم أثر ميزات أمان Power Platform على الحلول (DLP, BU, Roles) | `learn.wwl.design-power-platform-architectures` | مصفوفة أدوار المنسق والموظف في Dataverse | `PRACTICED` |
| تحديد استخدام الطرق الحتمية (Deterministic) أو غير الحتمية | `learn.wwl.design-power-platform-architectures` | قواعد الأهلية المحددة مقابل قرارات الذكاء الاصطناعي | `COVERED_THEORETICALLY` |
| اختيار واجهات الاستخدام (Code Apps, Generative Pages, PCF, MCP) | `learn.wwl.build-power-apps-experiences` | مقارنة مكونات PCF بتطبيقات Code Apps | `COVERED_THEORETICALLY` |
| تحديد متى يُستخدم Microsoft Foundry أو Copilot Studio للوكلاء | `learn.wwl.integrate-custom-agents-power-platform` | مذكرة مقارنة منصات بناء الوكلاء | `GAP` |

### 1.2 تصميم مكونات الحلول (Design solution components)
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| تصميم المكونات القابلة لإعادة الاستخدام (PCF, Client scripts) | `learn.wwl.build-power-apps-component-framework-code-components` | مكون اختيار حالة الأجهزة | `GAP` |
| تصميم الموصلات المخصصة وخوادم MCP (Custom Connectors & MCP) | `learn.wwl.consume-dataverse-mcp-servers` | خادم MCP لمخزون الأجهزة في المعمل 09 | `PRACTICED` |
| تصميم مكونات كود Dataverse (Plug-ins & Custom APIs) | `learn.wwl.implement-dataverse-plug-ins` | كتابة C# Plug-in وفهرسة Custom API في المعمل 01 | `VALIDATED` |
| تصميم الأتمتة (Power Automate & Copilot Studio) | `learn.wwl.implement-resilient-cloud-flows` | مسار اعتماد الأجهزة السحابي | `PRACTICED` |
| تصميم التكاملات الصادرة والواردة مع Azure | `learn.wwl.integrate-dataverse-external-services` | ربط Dataverse بخدمة Azure Service Bus | `GAP` |
| تصميم واجهات مخصصة عبر Power Apps Code Apps | `learn.wwl.build-dataverse-code-apps` | تطبيق تتبع الأجهزة في المعمل 04 | `PRACTICED` |
| تصميم المراقبة والتنبيهات عبر Azure Application Insights | `learn.wwl.deploy-operate-code-apps` | ربط تتبع الـ Plug-in والتطبيقات بـ App Insights | `GAP` |

### 1.3 إدارة دورة حياة التطبيقات (Implement ALM)
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| إدارة تبعيات الحلول وطبقاتها (Solution Dependencies & Layers) | `learn.wwl.deliver-solutions-governed-alm` | فحص طبقات الحلول وتجنب تعارضات غير المدارة | `PRACTICED` |
| إنشاء واستخدام متغيرات البيئة ومراجع الاتصال | `learn.wwl.deliver-solutions-governed-alm` | تخزين روابط الخدمات الخارجية كمتغيرات بيئة | `PRACTICED` |
| إعداد مسارات Power Platform Pipelines وأدوات البناء CI/CD | `learn.wwl.deliver-solutions-governed-alm` | أتمتة تصدير ونشر الحلول المدارة | `GAP` |

---

## المجال 2: توسيع تجربة المستخدم (25–30%)

### 2.1 تطبيق منطق الأعمال في Model-driven Apps عبر Client Scripting
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| كتابة كود يستهدف كائن Client API (`formContext`) | `learn.wwl.apply-client-logic-model-driven-apps` | سكربت نموذج طلب الأجهزة في المعمل 06 | `PRACTICED` |
| ضبط معالجات الأحداث وتسجيلها في النموذج | `learn.wwl.apply-client-logic-model-driven-apps` | ربط أحداث OnLoad و OnChange | `PRACTICED` |
| استدعاء Dataverse Web API من سكربت العميل | `learn.wwl.apply-client-logic-model-driven-apps` | استخدام `Xrm.WebApi.retrieveMultipleRecords` | `GAP` |
| تخصيص الأزرار والأوامر عبر Power Fx و JavaScript | `learn.wwl.apply-client-logic-model-driven-apps` | زر Reset lab data وزر طلب استثناء في النموذج | `PRACTICED` |
| إظهار مربعات الحوار والإشعارات عبر Client API | `learn.wwl.apply-client-logic-model-driven-apps` | `Xrm.Navigation.openAlertDialog` | `PRACTICED` |

### 2.2 إنشاء مكونات PCF البرمجية (Create PCF code components)
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| تطبيق أحداث دورة حياة المكون (`init`, `updateView`, `destroy`) | `learn.wwl.build-power-apps-component-framework-code-components` | مكون فحص حالة الجهاز المعمل 07 | `PRACTICED` |
| تهيئة ملف التكوين `ControlManifest.Input.xml` وتحديد الخصائص | `learn.wwl.build-power-apps-component-framework-code-components` | ربط خصائص الأعمدة بالمكون | `PRACTICED` |
| حزم ونشر واستهلاك المكون داخل Model-driven App | `learn.wwl.build-power-apps-component-framework-code-components` | استخدام أمر `pac pcf push` | `GAP` |

### 2.3 بناء وإدارة Power Apps Code Apps
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| ربط تطبيقات الكود بجداول Dataverse والخدمات السحابية | `learn.wwl.connect-code-apps-platform-services` | تطبيق المعمل 04 و 05 | `PRACTICED` |
| ضبط إعدادات أمان المحتوى (Content Security Policy - CSP) | `learn.wwl.deploy-operate-code-apps` | توثيق سياسات CSP لتطبيقات الكود | `GAP` |
| تشخيص ومراقبة تطبيقات الكود عبر أداة Monitor | `learn.wwl.deploy-operate-code-apps` | تتبع استدعاءات الشبكة والأداء | `GAP` |

---

## المجال 3: توسيع منصة Microsoft Power Platform على جانب الخادم (35–40%)

### 3.1 برمجة إضافات C# Dataverse Plug-ins
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| استخدام مراحل خط الأنابيب (PreValidation, PreOperation, PostOperation) | `learn.wwl.implement-dataverse-plug-ins` | معمل Lab 01 في مرحلة PreOperation | `VALIDATED` |
| قراءة واستخدام سياق التنفيذ (Execution Context) | `learn.wwl.implement-dataverse-plug-ins` | استخراج Target والحالة من السياق | `VALIDATED` |
| توظيف الصور القبلية والبعدية لدعم منطق الـ Plug-in | `learn.wwl.implement-dataverse-plug-ins` | تسجيل واستخدام `PreImage` لقراءة الحالة السابقة | `VALIDATED` |
| تنفيذ العمليات عبر Organization service داخل الـ Plug-in | `learn.wwl.implement-dataverse-plug-ins` | استدعاء `Retrieve` مع `ColumnSet` مقتصد | `VALIDATED` |
| تحسين أداء الـ Plug-in والالتزام بكونه عديم الحالة (Stateless) | `learn.wwl.harden-dataverse-extensions` | فحص الذاكرة وتجنب تخزين المتغيرات كحقول فئة | `VALIDATED` |
| تعريف وفهرسة Custom API وأحداث الأعمال Business Events | `learn.wwl.implement-dataverse-plug-ins` | تسجيل `eqp_IsEligibleForReplacement` كحدث أعمال | `VALIDATED` |
| تسجيل المكونات عبر أداة Plugin Registration Tool | `learn.wwl.implement-dataverse-plug-ins` | تسجيل تجميع C# وخطواته وصوره | `VALIDATED` |
| ضبط واستخدام الهوية المدارة (Managed Identity for Plug-ins) | `learn.wwl.harden-dataverse-extensions` | الاتصال بخدمات Azure دون أسرار ثابتة | `GAP` |

### 3.2 تنفيذ العمليات عبر Platform APIs
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| استدعاء Dataverse Web API عبر بروتوكول HTTP و C# | `learn.wwl.perform-dataverse-api-operations` | سكربت PowerShell في معمل 01 وتطبيق C# في معمل 02 | `VALIDATED` |
| استدعاء المنصة عبر SDK for .NET (`ServiceClient`) | `learn.wwl.perform-dataverse-api-operations` | مشروع `EquipmentApiExercise` في المعمل 02 | `PRACTICED` |
| تطبيق سياسات إعادة المحاولة عند تجاوز حدود الاستهلاك (Throttling) | `learn.wwl.diagnose-dataverse-api-failures` | استخدام Polly و `429 Too Many Requests` | `GAP` |
| ضبط واستكشاف أخطاء المصادقة عبر OAuth 2.0 و Azure Entra ID | `learn.wwl.perform-dataverse-api-operations` | استخراج رموز الوصول واستخدامها في الترويسات | `PRACTICED` |

### 3.3 معالجة الأحمال عبر Azure Functions
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| معالجة العمليات طويلة الأمد عبر دوال Azure | `learn.wwl.process-workloads-azure-functions` | مشروع `EquipmentRequestFunctions` في المعمل 03 | `PRACTICED` |
| بناء مشغلات مجدولة ومبنية على الأحداث (Timer & Event Triggers) | `learn.wwl.process-workloads-azure-functions` | استدعاء دالة التحقق عند تقديم طلب | `PRACTICED` |
| المصادقة مع Power Platform عبر Managed Identity | `learn.wwl.process-workloads-azure-functions` | الربط السحابي بدون مفاتيح مضمنة | `GAP` |

### 3.4 بناء وكلاء Microsoft Foundry و Copilot Studio و MCP
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| تكامل الوكلاء المخصصين عبر خوادم Dataverse MCP | `learn.wwl.consume-dataverse-mcp-servers` | تشغيل واستهلاك خادم MCP في المعمل 09 | `PRACTICED` |
| ربط الوكلاء ببيانات Dataverse واستدعاء الأدوات البرمجية | `learn.wwl.integrate-custom-agents-power-platform` | أتمتة استعلامات الأجهزة عبر وكيل ذكي | `GAP` |

---

## المجال 4: تطوير التكاملات المؤسسية (10–15%)

### 4.1 نشر واستهلاك أحداث Dataverse (Publish and consume events)
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| نشر الأحداث عبر `IServiceEndpointNotificationService` و PRT | `learn.wwl.publish-dataverse-events` | تسجيل نقاط نهاية الخدمة في PRT | `GAP` |
| تسجيل نقاط نهاية Webhooks و Azure Service Bus و Event Hubs | `learn.wwl.publish-dataverse-events` | إرسال إشعار للـ Service Bus عند تغيير حالة طلب | `GAP` |

### 4.2 مزامنة البيانات (Implement data synchronization)
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| مزامنة البيانات باستخدام تتبع التغييرات (Change Tracking) | `learn.wwl.synchronize-external-data-dataverse` | جلب التعديلات الجديدة فقط وتخزين الـ Token | `GAP` |
| كتابة كود يستخدم المفاتيح البديلة (Alternate Keys) | `learn.wwl.synchronize-external-data-dataverse` | تعريف مفتاح بديل على رقم الطلب واستخدامه في الاستعلام | `GAP` |
| مزامنة البيانات عبر رسالة `UpsertRequest` | `learn.wwl.synchronize-external-data-dataverse` | تحديث السجل إن وجد أو إنشاؤه في عملية واحدة | `GAP` |

### 4.3 إنشاء الموصلات المخصصة (Create custom connectors)
| الهدف الفرعي (Sub-Objective) | المرجع الرسمي / الموديول | الممارسة العملية والتطبيق | حالة التغطية |
| :--- | :--- | :--- | :---: |
| بناء وتوثيق موصل مخصص من مواصفة OpenAPI | `learn.wwl.build-power-platform-custom-connectors` | إنشاء موصل لخدمة المخزون | `GAP` |
| تطبيق قوالب السياسات (Policy Templates) لتعديل السلوك أثناء التشغيل | `learn.wwl.build-power-platform-custom-connectors` | تعديل ترويسات الاستدعاء ومسارات التوجيه | `GAP` |
