# مشروع المحفظة المؤسسي: نظام تخصيص وإدارة دورة حياة الأجهزة والمعدات
## Equipment Provisioning & Asset Lifecycle Management System

مشروع عملي مؤسسي مصمم لبناء وإثبات الكفاءة الهندسية الشاملة لمطور **Microsoft Power Platform & Dataverse** ينطلق من خلفية راسخة في **.NET / C#** ومعمارية الأنظمة السحابية.

---

## 1. نبذة عن السيناريو المؤسسي (Business Context)

تواجه المؤسسات الكبرى تحديات معقدة في إدارة دورة حياة الأجهزة التقنية والمعدات المخصصة للموظفين:
- طلبات استلام وتجديد الأجهزة (Laptops, Workstations, Mobile Devices, Specialized Lab Hardware).
- اعتماد الموازنات ومستويات الصلاحيات المتعددة (Manager Approval, IT Security Approval, Finance Verification).
- تتبع المخزون اللحظي ومنع الحجز المزدوج لنفس الأصل التقني (`Race Conditions & Double Allocation`).
- الفحص الفني، التسليم، استرجاع الأجهزة عند مغادرة الموظف، والصيانة الدورية.
- التكامل اللحظي مع أنظمة الموارد البشرية (HR System)، مراكز البيانات السحابية (Azure)، وسلاسل التوريد.

يوفر هذا المشروع نظاماً متكاملاً لإدارة هذه العمليات معتمداً على **Microsoft Dataverse** كنواة أمان ومعالجة بيانات مؤسسية، مع تسخير **C# / .NET** في المنطق المعقد ومعالجة المعاملات الحرجة، واستخدام **React / TypeScript** لواجهات المستخدم المتقدمة، و **Azure** للمعالجة غير المتزامنة وتوزيع الأحداث.

---

## 2. مصفوفة التقنيات والمعمارية (Architecture Stack)

| الطبقة الهندسية (Layer) | التقنيات المستخدمة (Technology Stack) | الدور الهندسي في المشروع |
|---|---|---|
| **قاعدة البيانات والمعاملات** | Microsoft Dataverse, Relational Schema, Alternate Keys | تخزين البيانات المؤسسية، تطبيق القيود العلائقية، نموذج الأمان متعدد المستويات (RBAC)، وتدقيق التغييرات (Auditing). |
| **منطق الخادم الحرج** | C# (.NET Framework 4.6.2 / .NET 8 Core), Dataverse SDK | إضافات `C# Plug-ins` للتحقق من المخزون، منع الحجز المتزامن، العمليات الحسابية المالية الدقيقة، و `Custom APIs`. |
| **التكامل الخارجي والخلفي** | .NET 8 Console / Worker Service, `Dataverse.ServiceClient` | مزامنة بيانات الأجهزة مع نظام الـ ERP الخارجي، تنفيذ العمليات المجمعة (`$batch`)، ومعالجة التزامن المتفائل بـ `ETags`. |
| **المعالجة السحابية والأحداث** | Azure Functions (Isolated Worker), Azure Service Bus | تفريغ العمليات الطويلة (تجهيز أنظمة التشغيل وحسابات المستخدمين)، واستقبال إشعارات خطافات الويب (`Webhooks`). |
| **واجهة الإدارة والعمليات** | Model-driven App, Custom Pages | لوحة التحكم المركزية لمديري تقنية المعلومات وفرق الدعم اللوجستي لإدارة السجلات وإجراءات العمل. |
| **مكونات الواجهة المخصصة** | PCF (Power Apps Component Framework), React, Fluent UI | عنصر تحكم تفاعلي ثلاثي الأبعاد لاختيار الأجهزة، فحص المواصفات، وتصور حالة المخزون بصرياً داخل النماذج. |
| **برمجة العميل المتقدمة** | TypeScript, Dataverse Client Scripting, FormContext | التحقق اللحظي من مدخلات النماذج، إخفاء وإظهار الحقول ديناميكياً، واستدعاءات الـ API غير المتزامنة. |
| **الأتمتة والذكاء الاصطناعي** | Power Automate Cloud Flows, Copilot Studio, MCP | مسارات تدفق الموافقات التفاعلية، وكيل ذكي مجيب لاستفسارات الموظفين عبر بروتوكول سياق النموذج (MCP). |
| **الجودة والنشر المستمر** | FakeXrmEasy, xUnit, PAC CLI, GitHub Actions / Azure DevOps | اختبارات الوحدة المعزولة دون اتصال بالخادم، التحقق الآلي من الحلول، ومسارات الترقية بين البيئات. |

---

## 3. هيكل مستودع المشروع (Repository Structure)

```text
portfolio/equipment-provisioning/
├── README.md                           # هذا المستند (نظرة عامة والسيناريو والقرارات الهندسية)
├── architecture/
│   ├── system-architecture.md          # مخطط المعمارية ومسار البيانات والحدود الأمنية
│   └── integration-patterns.md         # أنماط التكامل المتزامن وغير المتزامن
├── data-model/
│   ├── entity-relationship.md          # توصيف الجداول والعلاقات والمفاتيح البديلة
│   └── security-roles-matrix.md        # مصفوفة وحدات الأعمال وأدوار الأمان
├── dataverse/
│   ├── solutions/                      # الحلول المصدرة وملفات التخصيص
│   └── scripts/                        # سكربتات التهيئة عبر PAC CLI
├── plugins/
│   ├── src/                            # مشاريع C# Plug-in
│   └── tests/                          # اختبارات الوحدة باستخدام FakeXrmEasy
├── dotnet/
│   ├── sync-service/                   # خدمة مزامنة الأصول .NET 8 Worker Service
│   └── integration-cli/                # أدوات سطر الأوامر للاختبار المباشر
├── power-platform/
│   ├── client-scripts/                 # سكريبتات TypeScript الخاصة بنماذج Dataverse
│   ├── pcf-controls/                   # مشاريع مكونات PCF المبنية بـ React
│   └── apps/                           # تعريفات Model-driven App و Custom Pages
├── automation/
│   ├── cloud-flows/                    # توثيق وتصدير مسارات Power Automate
│   └── copilot/                        # إعدادات Copilot Studio و MCP Agent
├── tests/
│   ├── integration/                    # اختبارات التكامل الحية
│   └── e2e/                            # سيناريوهات التحقق الشاملة
└── technical-decisions/                # سجلات القرارات المعمارية (ADRs)
    ├── ADR-001-plugin-vs-flow.md
    └── ADR-002-azure-service-bus-decoupling.md
```

---

## 4. خطة الإنجاز عبر أسابيع المسار التعليمي (Milestone Mapping)

1. **المرحلة 1 (الأسابيع 1-3)**:
   - إنشاء حل Dataverse المؤسسي باسم `EquipmentProvisioning`.
   - نمذجة الجداول الأساسية (`Employee`, `Device`, `Equipment Request`, `Request Item`, `Approval History`).
   - ضبط العلاقات (`1:N` و `N:1` ذات الحذف المقيد والتعاقبي)، والمفاتيح البديلة (`Serial Number`).
2. **المرحلة 2 (الأسابيع 4-6)**:
   - كتابة وتطوير إضافة `ValidateDeviceAllocationPlugin` بـ C# في مرحلة `Pre-operation`.
   - كتابة إضافة `InventoryDeductionPlugin` لمنع التزامن في مرحلة `Post-operation`.
   - كتابة اختبارات وحدة معزولة بـ `FakeXrmEasy`.
3. **المرحلة 3 (الأسابيع 7-10)**:
   - بناء خدمة مزامنة الأصول بـ .NET 8 لربط النظام مع قاعدة بيانات خارجية.
   - إعداد دالة Azure Function لاستقبال أحداث الموافقة ومعالجة التجهيز الآلي.
4. **المرحلة 4 (الأسابيع 11-13)**:
   - كتابة سكريبت TypeScript لإدارة نموذج الطلب.
   - تطوير مكون PCF تفاعلي بـ React لعرض تفاصيل الأجهزة واختيارها بصرياً.
5. **المرحلة 5 (الأسابيع 14-17)**:
   - بناء مسارات التدفق التلقائية للموافقات عبر بريد وتطبيقات Teams.
   - بناء وكيل Copilot Studio متصل بـ MCP للإجابة على استفسارات الموظفين.
   - أتمتة البناء والنشر عبر GitHub Actions.
