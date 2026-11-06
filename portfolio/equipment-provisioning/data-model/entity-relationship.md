# نموذج البيانات ومخطط العلاقات العلائقية
## Relational Data Model, Schema & Entity-Relationship

تحدد هذه الوثيقة البنية الهيكلية لقاعدة البيانات المؤسسية لنظام **Equipment Provisioning & Asset Lifecycle Management System** المبني على **Microsoft Dataverse**، وتوضح الحقول، الأنواع، القيود، المفاتيح البديلة، وسلوكيات التعاقب (`Cascade Behaviors`).

بادئة التخصيص المعتمدة للحل المؤسسي: `ep_` (اختصار لـ *Equipment Provisioning*).

---

## 1. مخطط الكيانات والعلاقات (Entity-Relationship Diagram)

```mermaid
erDiagram
    EMPLOYEE ||--o{ EQUIPMENT_REQUEST : "يقدم (Submits 1:N)"
    EMPLOYEE ||--o{ ALLOCATION_HISTORY : "يُخصص له (Assigned To 1:N)"
    EMPLOYEE ||--o{ APPROVAL : "يعتمد (Approves 1:N)"
    
    DEVICE_MODEL ||--o{ DEVICE : "ينتمي إلى طراز (Model 1:N)"
    DEVICE_MODEL ||--o{ REQUEST_ITEM : "طراز مطلوب (Requested 1:N)"
    
    EQUIPMENT_REQUEST ||--|{ REQUEST_ITEM : "يتضمن بنود (Contains 1:N)"
    EQUIPMENT_REQUEST ||--o{ APPROVAL : "يتطلب اعتماد (Requires 1:N)"
    
    DEVICE ||--o{ REQUEST_ITEM : "يُخصص للبند (Allocated 1:N)"
    DEVICE ||--o{ ALLOCATION_HISTORY : "سجل حركات (History 1:N)"

    EMPLOYEE {
        guid ep_employeeid PK
        string ep_employeenumber UK "المفتاح البديل للربط مع HR"
        string ep_fullname "الاسم الكامل"
        string ep_email "البريد الإلكتروني"
        lookup ep_managerid FK "المدير المباشر (1:N Self-Ref)"
        lookup ep_departmentid FK "القسم / الإدارة"
        int ep_statuscode "حالة الموظف (Active, On-Leave, Terminated)"
    }

    DEVICE_MODEL {
        guid ep_devicemodelid PK
        string ep_modelcode UK "رمز الطراز"
        string ep_name "اسم الطراز"
        int ep_category "فئة الجهاز (Laptop, Desktop, Tablet, Accessory)"
        money ep_standardcost "التكلفة التقديرية الموحدة"
        int ep_warrantyperiodmonths "مدة الضمان بالشهور"
    }

    DEVICE {
        guid ep_deviceid PK
        string ep_serialnumber UK "الرقم التسلسلي الفريد (Alternate Key)"
        string ep_assetcode UK "رمز الأصل الثابت في الـ ERP"
        lookup ep_devicemodelid FK "الطراز"
        int ep_devicecondition "حالة الجهاز الفنية (New, Good, Refurbished, Defective)"
        int ep_allocationstatus "حالة التخصيص (In-Stock, Allocated, Reserved, Retired)"
        datetime ep_procurementdate "تاريخ الشراء"
        datetime ep_warrantyenddate "تاريخ انتهاء الضمان"
        lookup ep_currentassignedemployeeid FK "الموظف المخصص له حالياً"
    }

    EQUIPMENT_REQUEST {
        guid ep_equipmentrequestid PK
        string ep_requestnumber UK "رقم الطلب (Auto-Number: REQ-{SEQNUM:6})"
        lookup ep_requestingemployeeid FK "الموظف صاحب الطلب"
        int ep_requestpriority "الأولوية (Standard, Urgent, Executive)"
        int ep_approvalstatus "حالة الاعتماد (Draft, Submitted, Approved, Rejected)"
        int ep_fulfillmentstatus "حالة التسليم (Pending, In-Progress, Delivered, Cancelled)"
        money ep_totalestimatedcost "إجمالي التكلفة التقديرية (Rollup Column)"
        datetime ep_targetdeliverydate "تاريخ التسليم المستهدف"
    }

    REQUEST_ITEM {
        guid ep_requestitemid PK
        lookup ep_equipmentrequestid FK "الطلب الأب (Cascade Delete)"
        lookup ep_devicemodelid FK "طراز المعدة المطلوب"
        int ep_quantity "الكمية المطلوبة"
        lookup ep_allocateddeviceid FK "الجهاز الفعلي المخصص (من المخزون)"
        int ep_itemstatus "حالة البند (Requested, Reserved, Dispatched, Fulfilled)"
    }

    APPROVAL {
        guid ep_approvalid PK
        lookup ep_equipmentrequestid FK "الطلب المرتبط"
        lookup ep_approveremployeeid FK "الموظف المعتمد"
        int ep_approvalstage "مرحلة الاعتماد (Manager, IT Security, Finance)"
        int ep_decision "القرار (Pending, Approved, Rejected)"
        string ep_comments "ملاحظات الاعتماد"
        datetime ep_decisiondate "تاريخ اتخاذ القرار"
    }

    ALLOCATION_HISTORY {
        guid ep_allocationhistoryid PK
        lookup ep_deviceid FK "الجهاز"
        lookup ep_employeeid FK "الموظف"
        datetime ep_allocateddate "تاريخ التسليم والبدء"
        datetime ep_returneddate "تاريخ الاسترجاع الفعلي"
        int ep_returncondition "حالة الجهاز عند الاسترجاع"
        string ep_handovernotes "ملاحظات محضر التسليم والاستلام"
    }
```

---

## 2. المفاتيح البديلة والتحسين المؤسسي (Alternate Keys & Performance)

في التطوير الاحترافي عبر C# و Web API، لا يعتمد المهندس على الاستعلام المسبق لجلب معرفات الـ GUID لكل عملية استيراد، بل يستخدم **المفاتيح البديلة (`Alternate Keys`)** لتنفيذ عمليات التحديث أو الإدراج السريعة (`Upsert`).

| الجدول (Entity) | اسم المفتاح البديل (Key Logical Name) | حقول المفتاح البديل | الفائدة المعمارية للربط والتكامل |
|---|---|---|---|
| `ep_device` | `ep_key_device_serialnumber` | `ep_serialnumber` | يتيح لخدمة مزامنة الأصول بـ .NET تحديث حالة الجهاز مباشرة باستخدام الرقم التسلسلي دون الحاجة لاستعلام تمهيدي (`Upsert by Serial`). |
| `ep_device` | `ep_key_device_assetcode` | `ep_assetcode` | مطابقة الأصل الثابت مع سجلات الحسابات ونظام ERP المؤسسي. |
| `ep_employee` | `ep_key_employee_number` | `ep_employeenumber` | مزامنة بيانات الموظفين مع نظام إدارة الموارد البشرية (Workday / SAP HR) مباشرة. |
| `ep_devicemodel` | `ep_key_model_code` | `ep_modelcode` | سرعة فهرسة وتصنيف الأجهزة عند استيراد الكتالوج العام. |

---

## 3. سلوكيات التعاقب والعلاقات (Relationship Cascade Behaviors)

ضبط سلوكيات العلاقات في Dataverse أمر جوهري لمنع تلف البيانات وضمان حماية السجلات المحمية بالقانون:

1. **العلاقة بين `ep_equipmentrequest` و `ep_requestitem` (علاقة أب وابن - Parental)**:
   - *النوع*: `1:N`
   - *سلوك الحذف (Delete)*: **Cascade All** (إذا حُذف مسودة الطلب الأساسي، تُحذف تلقائياً كافة بنود الطلب المرتبطة به).
   - *سلوك التعيين (Assign / Share)*: **Cascade All** (تنتقل ملكية البنود مع الطلب الأساسي تلقائياً).

2. **العلاقة بين `ep_device` و `ep_requestitem` (علاقة مرجعية - Referential)**:
   - *النوع*: `1:N`
   - *سلوك الحذف (Delete)*: **Restrict Delete** (يُمنع منعاً باتاً حذف سجل الجهاز إذا كان مخصصاً لأي بند طلب تاريخي أو حالي، لضمان الحفاظ على السجلات المالية والأمنية).

3. **العلاقة بين `ep_device` و `ep_allocationhistory` (علاقة تتبع مرجعية)**:
   - *النوع*: `1:N`
   - *سلوك الحذف (Delete)*: **Restrict Delete** (يمنع حذف أصل الجهاز طالما أن له سجلات عهدة تاريخية).

---

## 4. أعمدة الحساب وأعمدة التجميع (Calculated & Rollup Columns)

1. **`ep_totalestimatedcost` في جدول `ep_equipmentrequest`**:
   - *النوع*: **Rollup Column** (عمود تجميعي).
   - *الصيغة*: تجميع مجموع (`SUM`) تكلفة بنود الطلب `ep_requestitem.ep_devicemodelid.ep_standardcost`.
   - *الفائدة*: يتيح لـ Dataverse ومسارات الموافقات معرفة إجمالي قيمة الطلب لتحديد مسار الاعتماد تلقائياً (مثلاً: إذا تجاوزت التكلفة 5,000 دولار تتطلب موافقة المدير المالي `Finance Approval`).

2. **`ep_iswarrantyactive` في جدول `ep_device`**:
   - *النوع*: **Calculated / Formula Column** (عمود صيغة بصيغة Power Fx).
   - *الصيغة*: `ep_warrantyenddate >= Now()`
   - *الفائدة*: تحديد فوري لما إذا كان الجهاز مشمولاً بالضمان دون الحاجة لتشغيل وظائف دورية في قاعدة البيانات.
