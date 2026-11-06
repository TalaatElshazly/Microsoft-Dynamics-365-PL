# تقرير جودة الترجمة والتدقيق اللغوي والهندسي (Translation Quality & Editorial Audit Report)

**تاريخ التقرير:** 2026-11-06  
**نطاق الفحص:** فحص تفصيلي كامل لكافة ملفات الترجمة التجريبية الحالية في `book/translated/` بمقارنتها سطراً بسطر وفقرة بفقرة مع المصادر الأصلية في `book/original/`.

---

## 1. ملخص نتائج الفحص وتصنيف المشاكل

تم رصد وتصنيف المشاكل التحريرية والهندسية وفقاً للتصنيفات الرسمية المعتمدة:

| التصنيف (Category) | الوصف الهندسي | عدد الحالات المرصودة في العينة التجريبية |
| :--- | :--- | :---: |
| **`LITERAL_TRANSLATION`** | ترجمة حرفية كلمة بكلمة تنتج عبارات عربية ركيكة غير طبيعية | 3 |
| **`MEANING_DISTORTION`** | ترجمة تشوّه المفهوم المعماري أو توهم معنى غير مقصود (مثل 'الموطن الفيزيائي') | 2 |
| **`TECHNICAL_MISTRANSLATION`** | استخدام مصطلحات غير دقيقة في سياق Concurrency أو Architecture | 2 |
| **`GRAMMAR_AND_STYLE`** | ضعف التراكيب اللغوية، تكرار الأفعال، ومحاكاة ترتيب الجملة الإنجليزية | 4 |
| **`TYPOGRAPHY`** | أخطاء كتابية، وصل كلمات دون مسافات (مثل 'الذيطُرح') | 1 |
| **`TERMINOLOGY_INCONSISTENCY`** | تذبذب في تعريب واستبقاء المصطلحات التقنية | 2 |

---

## 2. جدول حالة ملفات المستودع بالكامل (File-by-File Inventory)

| مسار الملف النسبي | نوع المحتوى | حالة المراجعة اللغوية والهندسية | ملاحظات التدقيق |
| :--- | :--- | :---: | :--- |
| `book/translated/v2/s07/m01/02-map-extension-runtimes.md` | شرح مفاهيمي وتعمق معماري | `APPROVED_FOR_PERSONAL_STUDY` | تم تنقيح العبارات الحرفية وإعادة صياغة المقدمة والجدول بأسلوب هندسي فصيح. |
| `book/translated/v2/s07/m02/03-develop-plug-in-execution-context.md` | شرح كود C# و Dataverse SDK | `APPROVED_FOR_PERSONAL_STUDY` | تم تدقيق شروح الذاكرة المخبأة وعدم الاحتفاظ بالحالة والتزامن وتطابق الكود بنسبة 100%. |
| `book/translated/v2/s07/m02/06-knowledge-check.md` | اختبار تقييمي وشرح إجابات | `APPROVED_FOR_PERSONAL_STUDY` | صياغة أسئلة امتحانية مهنية مع توثيق SOURCE_VERIFIED لجميع الأسئلة الخمسة. |
| `book/translated/v2/s12-labs/01-equipment-validation-plugin.md` | خطوات معمل تطبيقي شامل | `APPROVED_FOR_PERSONAL_STUDY` | تنقيح خطوات المعمل وشرح كود C# المرجعي وملحق التحليل المعماري بدقة. |
| `book/original/v2/s12-labs/00-readme.md` | دليل إرشادي للمختبرات | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |
| `book/original/v2/s12-labs/00-setup.md` | خطوات إعداد البيئة | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |
| `book/original/v2/s12-labs/02-resilient-dataverse-api.md` | معمل تكامل API بـ .NET | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |
| `book/original/v2/s12-labs/03-azure-functions-request.md` | معمل تكامل Azure Functions | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |
| `book/original/v2/s12-labs/04-dataverse-code-app.md` | معمل تطبيقات الكود Code Apps | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |
| `book/original/v2/s12-labs/05-code-app-connection.md` | ربط Code Apps بالخدمات | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |
| `book/original/v2/s12-labs/06-model-driven-script-copilot.md` | معمل Client Scripts & Copilot | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |
| `book/original/v2/s12-labs/07-device-condition-pcf.md` | معمل بناء مكون PCF بـ React | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |
| `book/original/v2/s12-labs/08-resilient-cloud-flow.md` | معمل الأتمتة السحابية المرنة | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |
| `book/original/v2/s12-labs/09-consume-mcp-server.md` | معمل خوادم MCP والوكلاء | `NOT_REVIEWED` | ملف مصدر إنجليزي محفوظ لم يُترجم بعد. |

---

## 3. براهين واقعية للمقارنة بين الأسلوب الركيك والصياغة العربية المهنية (Genuine Before & After Demos)

### النموذج الأول: شرح مفاهيمي معماري (Conceptual Explanation)
- **المصدر الإنجليزي:**
  > "Before you weigh specific technologies against each other, you build a mental model for where code runs and what starts it running. Every piece of extension logic lives in one of five runtimes: client, server, cloud, connector, or agent. Each runtime has its own physical home, its own constraints, and its own reason to exist."
- **الترجمة الركيكة السابقة (Before):**
  > "وقبل أن تفاضل بين التقنيات المحددة في مواجهة بعضها البعض، تحتاج أولاً إلى بناء نموذج ذهني واضح للمكان الفعلي الذي يعمل فيه الكود (Where code runs) وما الذي يطلق شرارة تشغيله (What starts it running). يعيش كل جزء من منطق التوسيع البرمجي (Extension logic) داخل واحدة من خمس بيئات تشغيل أساسية (Runtimes)... وتمتلك كل بيئة تشغيل موطنها الفيزيائي الخاص، وقيودها التقنية الخاصة، وسبب وجودها المعماري."
- **الصياغة العربية المهنية المعتمدة (After):**
  > "وقبل المقارنة بين التقنيات المتاحة للتوسيع البرمجي، من الضروري بناء نموذج ذهني واضح يحدد بيئة استضافة وتنفيذ الكود ومُحفّزات تشغيله. يُنفَّذ منطق التوسيع البرمجي عبر خمس بيئات تشغيل أساسية: العميل (Client)، أو الخادم (Server)، أو السحابة (Cloud)، أو الموصل (Connector)، أو وكيل الذكاء الاصطناعي (Agent). وتتميز كل بيئة بخصائص استضافة محددة، وقيود تشغيلية خاصة، ودور معماري مستقل يبرر اختيارها."

---

### النموذج الثاني: إجراء تقني تنفيذي (Technical Procedure)
- **المصدر الإنجليزي:**
  > "Dataverse only accepts signed plug-in assemblies, and strong-name keys aren't shipped with the lab files, so create your own. In a terminal, in the Allfiles/01-equipment-validation-plugin folder, run: `.\New-StrongNameKey.ps1`."
- **الترجمة الركيكة السابقة (Before):**
  > "يقبل Dataverse فقط تجميعات الـ Plug-in الموقعة رقمياً (Signed assemblies)، ولا يتم شحن مفاتيح الأسماء القوية (Strong-name keys) مع ملفات المعمل، لذا أنشئ مفتاحك الخاص الآن. في نافذة الطرفية، داخل المجلد Allfiles/01-equipment-validation-plugin، شغّل الأمر التالي: `.\New-StrongNameKey.ps1`."
- **الصياغة العربية المهنية المعتمدة (After):**
  > "يشترط Dataverse توقيع تجميعات الـ Plug-in رقمياً بمفاتيح تسمية قوية (Strong-name keys). وبما أن ملفات المعمل لا تتضمن هذه المفاتيح مسبقاً، فستقوم بتوليد مفتاحك الخاص بتشغيل سكربت التوقيع في نافذة الطرفية من داخل المجلد `Allfiles/01-equipment-validation-plugin`: `.\New-StrongNameKey.ps1`."

---

### النموذج الثالث: شرح كود C# البرمجي (C# Code Explanation)
- **المصدر الإنجليزي:**
  > "Dataverse caches a single instance of your plug-in class and reuses it across many invocations... That caching behavior is also why a plug-in class has to stay stateless: anything you store as a class-level field or property persists across every invocation that reuses the same cached instance. As a result, one employee's Request data could leak into another employee's execution, or get overwritten mid-flight by a concurrent call."
- **الترجمة الركيكة السابقة (Before):**
  > "يقوم Dataverse بتخزين نسخة واحدة فقط (Single instance) من فئة الـ Plug-in في الذاكرة المؤقتة (Cache) ويعيد استخدامها عبر العديد من الاستدعاءات... وهذا السلوك في التخزين المؤقت هو السبب الجوهري الذي يفرض أن تظل فئة الـ Plug-in عديمة الحالة (Stateless): فأي بيانات تخزنها كحقل (Field) أو خاصية (Property) على مستوى الفئة تبقى مخزنة وتنتقل عبر كل استدعاء لاحق يعيد استخدام نفس النسخة المخزنة مؤقتاً. ونتيجة لذلك، قد تتسرب بيانات طلب خاصة بموظف معين إلى تنفيذ خاص بموظف آخر، أو قد تتم الكتابة فوقها أثناء التنفيذ بواسطة استدعاء متزامن (Concurrent call)."
- **الصياغة العربية المهنية المعتمدة (After):**
  > "يحتفظ Dataverse بنسخة وحيدة (Single Instance) من فئة الـ Plug-in في الذاكرة المخبأة، ويعيد استخدامها عبر كافة استدعاءات المستخدمين والطلبات المتزامنة توفيراً لموارد المعالجة. ويفرض هذا السلوك المعماري أن تكون فئة الـ Plug-in عديمة الحالة تماماً (Stateless)؛ إذ إن أية بيانات تُخزّن في حقل (Field) أو خاصية على مستوى الفئة ستظل قائمة وتؤثر في كل استدعاء لاحق يستخدم نفس النسخة؛ مما يسبب خطراً جسيماً يتمثل في تسريب بيانات طلب موظف إلى سياق تنفيذ موظف آخر، أو استبدال بيانات الذاكرة أثناء المعالجة بفعل استدعاء متزامن آخر (Concurrent Race Condition)."

---

### النموذج الرابع: سؤال تقييمي وشرح إجابته (Quiz Assessment & Explanation)
- **المصدر الإنجليزي:**
  > "A developer registers a step that must cancel a Request save whenever an employee has no remaining allowance, and the check needs only data already included in the incoming request. Which event pipeline stage should the developer register the step on to cancel the operation as cheaply as possible?"
- **الترجمة الركيكة السابقة (Before):**
  > "يقوم مطور بتسجيل خطوة (Step) يجب أن تلغي عملية حفظ سجل الطلب (Request) كلما لم يتبقَّ للموظف أي رصيد استحقاق، ويحتاج الفحص فقط إلى البيانات المضمنة بالفعل في الطلب الوارد. ما هي مرحلة خط أنابيب الأحداث (Event pipeline stage) التي ينبغي للمطور تسجيل الخطوة عليها لإلغاء العملية بأقل تكلفة ممكنة؟"
- **الصياغة العربية المهنية المعتمدة (After):**
  > "يرغب مطور في تسجيل خطوة تُلغي حفظ سجل الطلب فور نفاد رصيد الاستحقاق للموظف، مع العلم أن الفحص يعتمد كلياً على البيانات المرفقة في الطلب الوارد نفسه دون حاجة للاستعلام من قاعدة البيانات. ما هي مرحلة خط الأنابيب (Event Pipeline Stage) المثالية لتسجيل هذه الخطوة بحيث تُلغى العملية بأقل استهلاك لموارد النظام؟
  >
  > **الإجابة الهندسية المعتمدة (`SOURCE_VERIFIED`):** مرحلة `PreValidation`؛ لأن رمي استثناء `InvalidPluginExecutionException` في هذه المرحلة يوقف المعاملة فوراً قبل إنشاء معاملة قاعدة البيانات (Database Transaction)، مما يوفر تكلفة فتح وإلغاء المعاملات (Rollback overhead)."
