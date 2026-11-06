# تحدي عملي (01): نمذجة بيانات مؤسسية وحل نزاعات التزامن في Dataverse
## Practical Challenge 01: Enterprise Data Modeling & Concurrency Control in Dataverse

- **المستوى**: متوسط - متقدم
- **الكود المرجعي**: `CHAL-DV-01`
- **المجال**: نمذجة Dataverse، المفاتيح البديلة، التزامن، وعلاقات الكيانات.
- **الوقت المقترح للإنجاز**: ساعتان.

---

## 1. سيناريو التحدي (Business Scenario)

طلب منك مدير البنية التحتية تصميم نموذج بيانات جديد داخل حل `EquipmentProvisioning` لإدارة **عقود الصيانة الدورية للأجهزة (Maintenance Service Contracts)** مع مورد خارجي (Third-Party Vendor).

### متطلبات العمل:
1. **التعاقد مع الموردين (`Vendor Maintenance Contract`)**:
   - لكل عقد رقم فريد صادر من المورد الخارجي (Vendor Contract Number).
   - العقد يغطي فترة زمنية محددة (تاريخ بدء وتاريخ انتهاء).
   - العقد يحدد قيمة مالية سنوية إجمالية وسقف أعلى لعدد الأجهزة المشمولة في الصيانة.
2. **ربط الأجهزة بالعقد (`Device Contract Coverage`)**:
   - يمكن للجهاز الواحد (`Device`) أن ينضم إلى عقد صيانة واحد فقط في نفس الوقت.
   - إذا تم إنهاء أو إلغاء العقد، يجب **ألا تُحذف** الأجهزة المرتبطة به مطلقاً، بل يتم فك الارتباط فقط (`Set Null`).
3. **التكامل البرمجي مع نظام المورد الخارجي عبر C# / Web API**:
   - يرسل المورد الخارجي يومياً ملف تحديث لحالة تغطية الأجهزة عبر واجهة Web API.
   - الملف لا يحتوي على معرفات Dataverse الفريدة (`GUIDs`)؛ بل يحتوي فقط على `Vendor Contract Number` و `Device Serial Number`.
   - يجب أن يدعم النظام تنفيذ عمليات التحديث والإدراج السريعة (`Upsert`) مباشرة بالاعتماد على هذه الحقول دون الحاجة لكتابة استعلامات تمهيدية لجلب الـ GUIDs.

---

## 2. المطلوب تنفيذه (Tasks & Deliverables)

1. **تصميم وتوصيف الجداول والأعمدة**:
   - حدد الجداول المطلوبة، نوع الملكية (`Organization` أم `User/Team`) مع التعليل المعماري.
   - حدد أنواع الأعمدة بدقة.
2. **تحديد المفاتيح البديلة (Alternate Keys)**:
   - حدد أسماء المفاتيح البديلة والحقول المكونة لها لضمان دعم سيناريو التكامل عبر Web API.
3. **تحديد نوع العلاقة وسلوكيات التعاقب (Cascade Behavior)**:
   - اشرح السلوك المعتمد في `Delete` و `Assign` و `Reparent`.
4. **كتابة كود C# تجريبي (Proof of Concept)**:
   - اكتب مقتطف كود C# باستخدام `Entity` و `EntityKeyControl` أو رابط OData Web API يوضح كيفية ربط جهاز بعقد باستخدام المفاتيح البديلة فقط:
     ```csharp
     // استدعاء Upsert باستخدام المفتاح البديل
     ```

---

## 3. معايير التقييم والحل النموذجي (Evaluation Criteria)

- **نوع الملكية المختار**:
  - جدول `Vendor Maintenance Contract` يجب أن يكون إما `Organization` إذا كانت العقود مركزية لجميع الفروع، أو `User/Team` إذا كانت الفروع تدير عقودها بشكل منفصل.
- **المفاتيح البديلة**:
  - تعريف `ep_key_vendor_contractnumber` على حقل `ep_vendorcontractnumber`.
  - الاعتماد على `ep_key_device_serialnumber` المعرف مسبقاً على جدول الأجهزة.
- **سلوك العلاقة**:
  - يجب ضبط سلوك الحذف على **Remove Link (Set Null)** لضمان عدم حذف سجلات الأجهزة عند حذف العقد (`Referential, Delete: Remove Link`).
- **صحة كود التكامل**:
  - استخدام `KeyAttributeCollection` في `EntityReference` في C# لتمثيل المفتاح البديل:
    ```csharp
    var contractRef = new EntityReference("ep_vendorcontract", "ep_vendorcontractnumber", "VEND-2026-XYZ");
    var deviceToUpdate = new Entity("ep_device", "ep_serialnumber", "SN-DELL-88392");
    deviceToUpdate["ep_maintenancecontractid"] = contractRef;
    service.Update(deviceToUpdate);
    ```
