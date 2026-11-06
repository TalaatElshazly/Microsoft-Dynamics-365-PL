# معمل 01: تأسيس جداول وعلاقات وأمان Dataverse (Milestone 1)
## Lab 01: Dataverse Foundations — Data Modeling, Relationships, Business Rules, and Security

هذا المعمل هو المحطة التطبيقية الأولى (Milestone 1) لتحويل التصميم النظري لنظام إدارة وتخصيص الأجهزة إلى بنية بيانات علائقية متكاملة داخل **Microsoft Dataverse**.

---

## 1. أهداف المعمل (Lab Objectives)
1. إنشاء حل Dataverse مؤسسي باسم `EquipmentProvisioning` وربطه بالناشر `ep_publisher`.
2. إنشاء الجداول الأساسية (`Device Model`, `Device`, `Equipment Request`, `Request Item`) وتحديد أنواع الملكية بدقة (`Organization-owned` مقابل `User/Team-owned`).
3. بناء العلاقات العلائقية وضبط سلوكيات الحذف والتعاقب (`Parental` مقابل `Referential with Restrict Delete`).
4. تفعيل وفهرسة المفتاح البديل (`Alternate Key`) على الرقم التسلسلي للجهاز (`ep_serialnumber`).
5. تطبيق قواعد العمل التصريحية (`Business Rules`) للتحقق من صحة المدخلات.
6. تصميم وضبط أدوار الأمان (`Security Roles`) لحماية البيانات وفق مبدأ الامتيازات الأدنى.
7. استخراج وتفكيك الحل المؤسسي إلى ملفات مصدرية داخل Git عبر أداة `pac solution unpack`.

---

## 2. جدول مقارنة أنواع الملكية (Ownership Architecture)

| الجدول المنشأ | نوع الملكية في Dataverse | المفهوم المقابل في أنظمة .NET | سبب الاختيار المعماري |
|---|---|---|---|
| `ep_devicemodel` | **Organization-Owned** | Global Reference / Lookup Data | كتالوج الأجهزة المعتمدة هو أصل عام موحد لكافة أقسام وفروع الشركة، لا يملكه موظف محدد ولا يتبع وحدة أعمال واحدة. |
| `ep_device` | **User/Team-Owned** | Asset Inventory with Custody Tracking | كل جهاز فيزيائي إما في عهدة موظف أو تحت إدارة فريق دعم فني محدد، ويتطلب تتبع صلاحيات وحدة الأعمال. |
| `ep_equipmentrequest` | **User/Team-Owned** | Transactional Document | الطلب يملكه الموظف الذي قدمه، ويتحكم نموذج الأمان في قدرته على رؤية وتعديل طلباته الخاصة فقط. |
| `ep_requestitem` | **User/Team-Owned** (Parental) | Aggregate Child Line Item | بند الطلب يتبع تماماً سجل الطلب الأب وينتقل معه في الصلاحيات والحذف. |

---

## 3. خطوات التنفيذ المعملية (Step-by-Step Implementation)

### الخطوة 1: إنشاء الحل في بيئة Dataverse
1. افتح بوابة صانع الحلول [make.powerapps.com](https://make.powerapps.com).
2. انتقل إلى قسم **Solutions** -> اضغط **New solution**.
3. املأ البيانات:
   - **Display name**: `Equipment Provisioning System`
   - **Name**: `EquipmentProvisioning`
   - **Publisher**: اختر الناشر الذي أنشأناه في المعمل السابق `Equipment Provisioning Publisher (ep)`.
   - **Version**: `1.0.0.0`
4. اضغط **Create** وافتح الحل الجديد.

---

### الخطوة 2: إنشاء جدول طراز الأجهزة (`ep_devicemodel`)
1. داخل الحل، اضغط **New** -> **Table** -> **Table**.
2. **Display name**: `Device Model`
3. **Plural name**: `Device Models`
4. في اللوحة الجانبية (Advanced options):
   - **Ownership**: اختر **Organization** (انتبه: لا يمكن تغيير نوع الملكية بعد إنشاء الجدول).
5. اضغط **Save**.
6. أضف الأعمدة التالية للجدول:
   - `ep_modelcode`: Single line of text, Required, Max length 50.
   - `ep_category`: Choice (خيارات: `Laptop`=10000, `Desktop`=10001, `Monitor`=10002, `Accessory`=10003).
   - `ep_standardcost`: Currency, Minimum 0, Precision 2.
   - `ep_warrantyperiodmonths`: Whole number, Minimum 0, Maximum 120.

---

### الخطوة 3: إنشاء جدول الأجهزة الفردية والمفتاح البديل (`ep_device`)
1. أنشئ جدولاً جديداً:
   - **Display name**: `Device`
   - **Plural name**: `Devices`
   - **Ownership**: **User or team**
2. أضف الأعمدة التالية:
   - `ep_serialnumber`: Single line of text, Required (الرقم التسلسلي من المصنع).
   - `ep_assetcode`: Single line of text, Optional (رمز الأصل المحاسبي).
   - `ep_allocationstatus`: Choice (`In-Stock`=10000, `Allocated`=10001, `Maintenance`=10002, `Retired`=10003).
   - `ep_condition`: Choice (`New`=10000, `Good`=10001, `Damaged`=10002).
   - `ep_procurementdate`: Date only.
   - `ep_warrantyenddate`: Date only.
3. **إعداد العلاقة مع طراز الجهاز**:
   - أضف عمود بحث (Lookup) باسم `ep_devicemodelid` يشير إلى جدول `Device Model`.
4. **تفعيل المفتاح البديل (Alternate Key)**:
   - انتقل إلى علامة تبويب **Keys** داخل جدول `Device`.
   - اضغط **New key**.
   - **Display name**: `Device Serial Number Key`
   - **Name**: `ep_key_device_serialnumber`
   - حدد حقل: `ep_serialnumber`.
   - اضغط **Save**.
   - *ملاحظة معمارية*: ستبدأ خدمة فهرسة خلفية في Dataverse؛ انتظر حتى تتحول حالة المفتاح إلى **Active**. هذا المفتاح هو ما سيمكننا لاحقاً من عمل `Upsert` عبر C# دون استعلام مسبق.

---

### الخطوة 4: إنشاء جدول الطلبات (`ep_equipmentrequest`) وبنود الطلب (`ep_requestitem`)
1. **جدول الطلبات (`ep_equipmentrequest`)**:
   - **Ownership**: **User or team**
   - العمود الأساسي `ep_requestnumber`: اضغط على خيارات العمود واختر النوع **Autonumber** بتنسيق مخصص: `REQ-{SEQNUM:6}`.
   - `ep_requestpriority`: Choice (`Standard`=10000, `Urgent`=10001, `Executive`=10002).
   - `ep_approvalstatus`: Choice (`Draft`=10000, `Submitted`=10001, `Approved`=10002, `Rejected`=10003).
   - `ep_fulfillmentstatus`: Choice (`Pending`=10000, `In-Progress`=10001, `Fulfilled`=10002, `Cancelled`=10003).
   - `ep_targetdeliverydate`: Date only.
2. **جدول بنود الطلب (`ep_requestitem`) وعلاقة الأب والابن**:
   - أنشئ جدول `Request Item` بنوع ملكية **User or team**.
   - أضف عمود بحث `ep_equipmentrequestid` يشير إلى جدول `Equipment Request`.
   - في خيارات العلاقة المتقدمة:
     - اختر نوع السلوك: **Parental**. (هذا يضمن أن حذف الطلب يحذف بنوده تلقائياً `Cascade All`).
   - أضف عمود بحث `ep_devicemodelid` يشير إلى جدول `Device Model`.
   - أضف عمود بحث `ep_allocateddeviceid` يشير إلى جدول `Device` (اختر سلوك العلاقة: **Configurable Cascading -> Delete: Restrict** لمنع حذف أي جهاز مخصص لبند طلب).
   - `ep_quantity`: Whole number, Default value = 1.

---

### الخطوة 5: تطبيق قاعدة عمل (Business Rule) لتحديد موعد التسليم
نريد تطبيق قاعدة عمل على مستوى الخادم والعميل: إذا تم تحديد أولوية الطلب على أنها `Urgent` أو `Executive`، يجب ألا يتجاوز تاريخ التسليم المستهدف 3 أيام من تاريخ اليوم:

1. افتح جدول `Equipment Request` -> انتقل إلى علامة تبويب **Business Rules** -> اضغط **Add business rule**.
2. في مصمم قواعد العمل:
   - اضغط على الشرط وضعه كالتالي:
     - `ep_requestpriority` Equals `Urgent` OR `ep_requestpriority` Equals `Executive`
   - في مسار التحقق الإيجابي (True):
     - أضف إجراء **Show Error Message** إذا كان `ep_targetdeliverydate` فارغاً بنص: *"يجب تحديد موعد تسليم استثنائي للطلبات العاجلة والتنفيذية"*.
     - أو أضف إجراء **Set Field Value** لتعيين الحقول الإلزامية.
3. في الزاوية العلوية، غير نطاق التنفيذ من *Scope: All Forms* إلى **Scope: Entity** (هذا يضمن تشغيل قاعدة العمل حتى لو تم إنشاء السجل عبر C# Web API أو Power Automate وليس فقط عبر واجهة المستخدم!).
4. اضغط **Save** ثم **Activate**.

---

### الخطوة 6: إنشاء أدوار الأمان (Security Roles)
1. في حل `EquipmentProvisioning`، اضغط **New** -> **Security** -> **Security role**.
2. أنشئ الدور الأول: `Equipment Requester`:
   - جدول `Equipment Request`:
     - Create: **User** (دائرة ربعية)
     - Read: **User**
     - Write: **User** (طالما في حالة مسودة)
     - Delete: **User**
   - جدول `Request Item`:
     - Create, Read, Write, Delete: **User**
   - جدول `Device Model`:
     - Read: **Organization** (دائرة كاملة خضراء ليرى كافة الطرازات المتاحة)
3. أنشئ الدور الثاني: `IT Asset Manager`:
   - جداول `Device`, `Device Model`, `Equipment Request`, `Request Item`:
     - جميع الامتيازات (Create, Read, Write, Delete, Assign, Share): **Organization**.

---

### الخطوة 7: تفكيك الحل وتصديره إلى Git عبر PAC CLI
الآن نقوم بسحب الحل السحابي إلى محطة التطوير وتفكيكه تمهيداً لرفعه إلى مستودع الشيفرات:

```powershell
# الانتقال إلى مسار التخزين
cd "e:\Microsoft Dynamics\portfolio\equipment-provisioning\dataverse"

# تصدير الحل غير المدار من السحابة كملف مضغوط
pac solution export --name "EquipmentProvisioning" --path "EquipmentProvisioning.zip"

# تفكيك ملف الحل إلى ملفات XML قابلة للتتبع في Git
pac solution unpack --zipfile "EquipmentProvisioning.zip" --folder "src"

# فحص الملفات الناتجة داخل src/Entities
dir src/Entities
```

---

## 4. شروط القبول والتحقق الهندسي (Acceptance Criteria)

- [ ] تم إنشاء الحل بنجاح وربطه بالناشر المعتمد `ep_publisher`.
- [ ] جدول `ep_devicemodel` منشأ بنوع ملكية `Organization-owned`.
- [ ] جدول `ep_device` يحتوي على المفتاح البديل `ep_key_device_serialnumber` في حالة نشطة (`Active`).
- [ ] العلاقة بين `Equipment Request` و `Request Item` من نوع `Parental`.
- [ ] العلاقة بين `Device` و `Request Item` تطبق قيد منع الحذف `Restrict Delete`.
- [ ] قاعدة العمل مطبقة على نطاق الكيان بالكامل (`Entity Scope`).
- [ ] تم إنشاء دوري الأمان `Equipment Requester` و `IT Asset Manager` وفق صلاحيات دقيقة.
- [ ] مجلد `dataverse/src/Entities` يحتوي على ملفات التوصيف المفككة بصيغة XML في مستودع Git.
