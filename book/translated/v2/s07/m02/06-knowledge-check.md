# تقييم الموديول (Module Assessment)


## اختبر معلوماتك (Check your knowledge)

1. يرغب مطور في تسجيل خطوة تلغي حفظ سجل الطلب (Request) فور نفاد رصيد الاستحقاق للموظف، علماً بأن الفحص يعتمد حصراً على البيانات المتوفرة في الطلب الوارد نفسه. ما هي مرحلة خط أنابيب الأحداث (Event pipeline stage) التي ينبغي للمطور تسجيل الخطوة عليها لإلغاء العملية بأقل تكلفة ممكنة؟

   - [ ] PreOperation

   - [ ] PreValidation

   - [ ] PostOperation

2. تقوم فئة Plug-in بتخزين سياق التنفيذ (ExecutionContext) في حقل خاص (Private field) على مستوى الفئة لكي تتمكن دالة مساعدة (Helper method) من قراءته لاحقاً داخل نفس الفئة. لماذا يتسبب هذا التصميم في مشاكل خطيرة في بيئة الإنتاج؟

   - [ ] لا يمكن قراءة سياق التنفيذ إلا مرة واحدة فقط لكل تجميع (Assembly) خاص بالـ Plug-in، ولذلك فإن تخزينه في حقل يستنفد تلك القراءة الوحيدة.

   - [ ] الحقول المعرفة على فئة الـ Plug-in تكون مرئية فقط لخدمة المؤسسة (Organization service)، لذا لن تتمكن الدالة المساعدة في نفس الفئة من قراءتها على أي حال.

   - [ ] يقوم Dataverse بتخزين نسخة واحدة فقط من فئة الـ Plug-in في الذاكرة المؤقتة (Cache) وإعادة استخدامها عبر العديد من الاستدعاءات، لذا فإن الحقل المخزن يمكن أن يسرب البيانات بين طلبات غير مرتبطة ببعضها.

3. يحتاج Plug-in مسجل في مرحلة PostOperation على رسالة التحديث (Update) إلى مقارنة قيمة عمود قبل التحديث بالقيمة التي أنتجتها العملية الرئيسية. ما هو الأسلوب الذي يوفر القيمتين معاً؟

   - [ ] تسجيل صورة قبلية (Pre-image) وصورة بعدية (Post-image) على الخطوة، ومقارنة الاسمين المستعارين (Aliases) داخل الـ Plug-in.

   - [ ] قراءة المجموعة InputParameters مرتين، مرة قبل استدعاء خدمة المؤسسة (Organization service) ومرة بعد استدعائها.

   - [ ] زيادة ترتيب تنفيذ الخطوة (Execution order) بحيث تعمل بعد جميع الخطوات الأخرى المسجلة على نفس الرسالة.

4. يحتاج Plug-in مسجل في مرحلة PostOperation إلى تحديث صف في جدول آخر كجزء من نفس المعاملة (Transaction) التي أطلقته. ما هو الأسلوب الصحيح لإنجاز ذلك من داخل الـ Plug-in؟

   - [ ] استدعاء واجهة Dataverse Web API باستخدام عميل HTTP، نظراً لأن الـ Plug-in يعمل بالفعل ضمن سياق مصادق عليه.

   - [ ] إضافة أعمدة الجدول الآخر إلى خصائص التصفية (Filtering attributes) الخاصة بالخطوة الحالية لكي يقوم Dataverse بتحديثها تلقائياً.

   - [ ] الحصول على نسخة من IOrganizationService عبر المصنع IOrganizationServiceFactory واستدعاء دالة Update الخاصة بها.

5. أثناء تسجيل تجميع إضافة برمجية (Plug-in assembly) باستخدام أداة Plugin Registration Tool لبيئة Dataverse سحابية (Online)، ما هو وضع العزل (Isolation mode)وموقع التخزين (Location) اللذان يجب على المطور اختيارهما؟

   - [ ] وضع العزل None مع تخزين التجميع على القرص الصلب للخادم (Server's disk).

   - [ ] وضع العزل Sandbox مع تخزين التجميع في قاعدة البيانات (Database).

   - [ ] وضع العزل Sandbox مع تخزين التجميع في ذاكرة التجميعات العمومية (Global Assembly Cache - GAC).

<!-- study-aid-answer-key-start -->
> [!NOTE]
> **مفتاح الإجابات المرجعي وحالة التحقق (`Answer Key & Verification Status`):**
> *(ملاحظة منهجية: واجهة Markdown الثابتة في Microsoft Learn تعرض نص الأسئلة والاختيارات فقط دون حقل الإجابة الصحيحة؛ وقد تم التحقق من كل إجابة أدناه بمقابلتها نصياً مع الفقرات الرسمية في وحدات نفس الموديول `learn.wwl.implement-dataverse-plug-ins`).*
> - **السؤال 1 — الإجابة:** `PreValidation` | **حالة التحقق:** `SOURCE_VERIFIED` (موثق نصياً في الوحدة 2: *"If that check runs in PreValidation and throws an exception, Dataverse cancels the Request before any transaction exists, which is inexpensive and immediate"*).
> - **السؤال 2 — الإجابة:** `Dataverse caches and reuses a single instance of the plug-in class across many invocations, so a stored field can leak data between unrelated requests.` | **حالة التحقق:** `SOURCE_VERIFIED` (موثق نصياً في الوحدة 3، قسم *Keep your plug-in class stateless*: *"Dataverse caches a single instance of your plug-in class and reuses it across many invocations... one employee's Request data could leak into another employee's execution"*).
> - **السؤال 3 — الإجابة:** `Register a pre-image and a post-image on the step, and compare the two aliases inside the plug-in.` | **حالة التحقق:** `SOURCE_VERIFIED` (موثق نصياً في الوحدة 4، قسم *Compare pre-image and post-image values*).
> - **السؤال 4 — الإجابة:** `Obtain an IOrganizationService instance from the IOrganizationServiceFactory and call its Update method.` | **حالة التحقق:** `SOURCE_VERIFIED` (موثق نصياً في الوحدة 4، قسم *Use the Organization service inside a plug-in*).
> - **السؤال 5 — الإجابة:** `Sandbox isolation mode with the assembly stored in the database.` | **حالة التحقق:** `SOURCE_VERIFIED` (موثق نصياً في الوحدة 5 وفي خطوة التسجيل رقم 4 في المعمل العملي `Lab 01`: *"Confirm Isolation Mode is Sandbox and Location is Database"*).
<!-- study-aid-answer-key-end -->