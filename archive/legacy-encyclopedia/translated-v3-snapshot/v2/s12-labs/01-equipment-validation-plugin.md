# بناء وتسجيل إضافة برمجية (Plug-in) للتحقق من أهلية المعدات


يُعد حل تجهيز المعدات (**Equipment Provisioning**) حلاً مبنياً على منصة Microsoft Dataverse يتيح للموظفين طلب معدات بديلة، ويتيح للمنسقين مراجعة تلك الطلبات واعتمادها. ولا يُسمح باستبدال أي جهاز إلا إذا كان قد مضى على إصدار الجهاز المراد استبداله **24** شهراً على الأقل، أو تم تمييزه بأنه تالف وغير قابل للإصلاح — ولكن في الوضع الحالي يتم فرض هذه القاعدة فقط بواسطة سكربت على نموذج الطلب (Form script)، مما يعني أنه يمكن تجاوزها بسهولة بواسطة أي شخص يقوم بتحديث الطلب مباشرة عبر واجهة Dataverse Web API بدلاً من واجهة النموذج.

في هذا التمرين العملي، ستكتب وتسجل إضافة برمجية (Dataverse Plug-in) تفرض نفس القاعدة على الخادم (Server) حيث لا يمكن تجاوزها أبداً. ستستخدم حزمة تطوير البرمجيات Dataverse SDK for .NET، وصورة قبلية (Pre-image) لقراءة الحالة السابقة للطلب، وخدمة المؤسسة (Organization service) للبحث عن الجهاز المراد استبداله. ثم ستقوم بتسجيل الـ Plug-in باستخدام أداة Plugin Registration Tool، وتثبت عملياً أنه يغلق الثغرة التي تركها الفحص المقتصر على النموذج مفتوحة. وأخيراً، ستقوم بفهرسة الواجهة البرمجية المخصصة (Custom API) الخاصة بالقاعدة كحدث أعمال (Business event) في Dataverse لكي تتمكن مسارات الأتمتة الأخرى من اكتشافه والتفاعل معه.

في هذا التمرين، ستقوم بما يلي:

- محاولة اعتماد طلب غير مؤهل مباشرة عبر واجهة Dataverse Web API متجاوزاً فحص جانب العميل في النموذج
- كتابة Plug-in يقرأ صورة قبلية (Pre-image) ويستعلم من Dataverse عبر Organization service لفرض قاعدة الأهلية
- تسجيل الـ Plug-in باستخدام أداة Plugin Registration Tool
- التأكد من أن الـ Plug-in يمنع نفس محاولة التجاوز التي نجحت سابقاً — مع استمرار السماح بالحالات الاستثنائية المشروعة
- فهرسة الـ Custom API الخاصة بقاعدة الأهلية كحدث أعمال (Dataverse business event)

يستغرق إكمال هذا التمرين حوالي **35** دقيقة تقريباً.

## المتطلبات الأساسية (Prerequisites)

لإكمال هذا التمرين، تحتاج إلى:

- جهاز كمبيوتر يعمل بنظام Windows؛ إذ إن Visual Studio وأداة Plugin Registration Tool هما تطبيقا سطح مكتب يعملان على Windows فقط، ولا يوجد بديل عابر للمنصات لهذا التمرين.
- برنامج [Visual Studio](https://visualstudio.microsoft.com/){:target="_blank"} على الرابط `https://visualstudio.microsoft.com/`، إصدار 2022 أو أحدث، مع توفر قالب المشروع **Class Library (.NET Framework)** (الذي يُثبَّت ضمن حزمة العمل **.NET desktop development**).
- حزمة الاستهداف .NET Framework 4.8 targeting pack؛ وإذا لم تكن مثبتة مسبقاً، فسيطالبك Visual Studio بتثبيتها في أول مرة تبني فيها مشروعاً يستهدف هذا الإصدار.
- أداة سطر الأوامر [Power Platform CLI](https://learn.microsoft.com/power-platform/developer/cli/introduction){:target="_blank"} على الرابط `https://learn.microsoft.com/power-platform/developer/cli/introduction`، وتُستخدم لتشغيل أداة Plugin Registration Tool.
- أداة سطر الأوامر [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli){:target="_blank"} على الرابط `https://learn.microsoft.com/cli/azure/install-azure-cli`، وتُستخدم في هذا التمرين للحصول على رمز وصول (Access token) لإجراء استدعاء مباشر لواجهة Web API.
- بيئة Dataverse تمتلك فيها دور الأمان (Security Role) إما **System Administrator** أو **System Customizer**؛ ويمتلك مالك البيئة التطويرية هذا الدور افتراضياً.

> **Note**: إذا كان مساعد GitHub Copilot متاحاً لديك داخل Visual Studio، فلا تتردد في استخدامه للمساعدة في صياغة أو مراجعة كود الـ Plug-in في هذا التمرين — ولكنه غير إلزامي، فجميع مقاطع الكود التي تحتاجها متوفرة بالكامل هنا.

## قبل أن تبدأ (Before you start)

يفترض هذا التمرين أن لديك بالفعل بيئة تطوير Dataverse مثبتاً عليها الحل الأساسي **Equipment Provisioning (base)**، كما هو موضح في دليل الإعداد [Set up your lab environment](./00-setup.md). إذا لم تكن قد أكملت ذلك الإعداد بعد، فقم بإنجازه الآن قبل المتابعة.

1. سجّل الدخول إلى [بوابة صانع Power Apps (Power Apps maker portal)](https://make.powerapps.com){:target="_blank"} على الرابط `https://make.powerapps.com`، وتأكد من أن محدد البيئة يعرض البيئة التي تستخدمها لهذه التمارين.

1. اختر **Solutions**، وتأكد من ظهور الحل **Equipment Provisioning (base)** في القائمة. إذا لم يكن ظاهراً، فاتبع خطوات الاستيراد الواردة في [Set up your lab environment](./00-setup.md)، ثم عد إلى هنا.

1. قم بتنزيل ملف الحل المدار [EquipmentProvisioningLab01_managed.zip](https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/EquipmentProvisioningLab01_managed.zip){:target="_blank"} من الرابط `https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/EquipmentProvisioningLab01_managed.zip`. يضيف هذا الحل نموذج **Request intake** إلى جدول الطلبات (Request table) محتوياً على فحص الأهلية في جانب العميل الذي ستقوم بتجاوزه في المهمة التالية.

1. في صفحة **Solutions**، اختر **Import solution**، ثم اختر **Browse**، وحدد الملف الذي قمت بتنزيله، واضغط على **Next** ثم **Import**. انتظر حتى يكتمل الاستيراد.

1. افتح تطبيق **Equipment Provisioning** واختر **Requests** من خريطة الموقع (Site map).

1. في شريط الأوامر (Command Bar) الخاص بطريقة العرض **Active Requests**، اختر الزر **Reset lab data**. انتظر حتى ينتهي، وراجع الملخص في نافذة الحوار **Lab data reset**، ثم أغلق النافذة واختر **Refresh**.

   ينبغي أن ترى الطلبات من `REQ-SEED-001` إلى `REQ-SEED-004` مدرجة كطلبات مفتوحة، وكل منها يحمل الحالة الموضحة في ملخص البيانات.

## محاولة اعتماد طلب غير مؤهل (Try to approve an ineligible request)

قبل أن تكتب أي سطر كود، شاهد بنفسك الثغرة المعمارية التي توشك على إغلاقها. يطلب السجل `REQ-SEED-001` استبدال جهاز كمبيوتر محمول تم إصداره منذ 8 أشهر فقط وليس تالفاً — وبالتالي لا ينبغي أن يكون مؤهلاً للاستبدال قبل مرور 16 شهراً أخرى. ويمنع فحص جانب العميل على نموذج الطلب المنسقَ من اعتماده عن طريق الخطأ، ولكن ذلك الفحص يعمل داخل المتصفح فقط.

1. في تطبيق **Equipment Provisioning**، افتح السجل `REQ-SEED-001`.

1. اختر محدد النموذج (Form selector) في أعلى السجل (الذي يعرض اسم النموذج الحالي)، وقم بالتبديل إلى النموذج **Request intake**.

1. اضبط حقل **Request status** على القيمة **Approved**، ثم احفظ السجل.

   ينبغي أن يظهر لك إشعار على النموذج مشابه للرسالة: *This device was issued on {date}, less than 24 months ago, and isn't damaged beyond repair. The request can't be approved yet.* يتم منع الحفظ، وتظل قيمة **Request status** على الحالة **Submitted**.

1. اختر أيقونة الترس (**Settings**) في الزاوية العلوية اليمنى من بوابة الصانع، ثم اختر **Developer resources**. انسخ قيمة **Web API endpoint** — حيث ستستخدمها كعنوان URL للبيئة في بقية خطوات هذا التمرين.

1. قم بتنزيل السكربت [Approve-RequestViaWebApi.ps1](https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/Approve-RequestViaWebApi.ps1){:target="_blank"} من الرابط `https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/Approve-RequestViaWebApi.ps1`. يحصل هذا السكربت على رمز وصول لبيئتك باستخدام Azure CLI، ثم يرسل نفس تغيير الحالة مباشرة إلى واجهة Dataverse Web API — بدون المرور على أي نموذج أو فحص على جانب العميل.

1. في نافذة الطرفية (Terminal)، سجّل الدخول إلى Azure CLI باستخدام بيانات اعتمادك. يتيح لك الخيار `--allow-no-subscriptions` تسجيل الدخول حتى لو لم يكن لحسابك اشتراك Azure فعال؛ فهذا السكربت يحتاج فقط إلى صلاحية الوصول إلى بيئة Power Platform الخاصة بك:

    ```powershell
    az login --allow-no-subscriptions
    ```

    > **Note**: إذا كنت تستخدم Azure CLI مع أكثر من حساب، فسجّل الدخول بالحساب الذي تستخدمه لبيئة Power Platform الخاصة بك. وإذا كان ذلك الحساب ينتمي إلى مستأجر (Tenant) مختلف عن مستأجرك المعتاد، فأضف المعامل `--tenant` متبوعاً باسم النطاق الخاص بالمستأجر.

1. قم بتشغيل السكربت مع تمرير عنوان URL للبيئة الذي نسخته ورقم الطلب:

    ```powershell
    .\Approve-RequestViaWebApi.ps1 -EnvironmentUrl "<your environment URL>" -RequestNumber "REQ-SEED-001"
    ```

1. ارجع إلى تطبيق **Equipment Provisioning** وقم بتحديث (Refresh) السجل `REQ-SEED-001`.

   ستلاحظ أن قيمة **Request status** أصبحت الآن **Approved** — أي إن نفس التغيير الذي منعه النموذج قبل لحظات قد نجح تنفيذه عبر واجهة Web API. هذه هي الثغرة التي ستغلقها بقية خطوات التمرين.

## تنفيذ قاعدة الأهلية داخل الـ Plug-in

لا يمكن لأي سكربت على جانب العميل إغلاق هذه الثغرة بمفرده أبداً، لأنه يعمل فقط عند حفظ النموذج داخل المتصفح. أنت بحاجة إلى Plug-in: أي كود يقوم خادم Dataverse نفسه بتشغيله كلما تم تحديث سجل طلب، بغض النظر عن العميل أو الأداة التي أجرت التغيير.

تتضمن ملفات المعمل التي قمت باستنساخها أثناء الإعداد مشروع بداية جاهزاً في المسار `Allfiles/01-equipment-validation-plugin/AB400.Lab01`. ويشير هذا المشروع مسبقاً إلى حزمة `Microsoft.CrmSdk.CoreAssemblies` ويحتوي على فئة Plug-in مبدئية بها تعليقات توضح المكان الذي ستضع فيه الكود الخاص بك. وإذا لم تكن قد استنسخت المستودع بالكامل، فقم بتنزيل هذه الملفات بشكل فردي مع الحفاظ على نفس هيكل المجلدات:

- ملف المشروع [AB400.Lab01.csproj](https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/AB400.Lab01/AB400.Lab01.csproj){:target="_blank"} من `https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/AB400.Lab01/AB400.Lab01.csproj`، وضعه داخل مجلد باسم `AB400.Lab01`
- ملف الفئة [RequestApprovalPlugin.cs](https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/AB400.Lab01/RequestApprovalPlugin.cs){:target="_blank"} من `https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/AB400.Lab01/RequestApprovalPlugin.cs`، وضعه داخل نفس المجلد `AB400.Lab01`
- سكربت التوقيع [New-StrongNameKey.ps1](https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/New-StrongNameKey.ps1){:target="_blank"} من `https://raw.githubusercontent.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/main/Allfiles/01-equipment-validation-plugin/New-StrongNameKey.ps1`، وضعه في المجلد الأب الذي يحتوي على المجلد `AB400.Lab01`

1. يقبل Dataverse فقط تجميعات الـ Plug-in الموقعة رقمياً (Signed assemblies)، ولا يتم شحن مفاتيح الأسماء القوية (Strong-name keys) مع ملفات المعمل، لذا أنشئ مفتاحك الخاص الآن. في نافذة الطرفية، داخل المجلد `Allfiles/01-equipment-validation-plugin`، شغّل الأمر التالي:

    ```powershell
    .\New-StrongNameKey.ps1
    ```

    ينشئ هذا السكربت الملف `AB400.Lab01\AB400.Lab01.snk`، وهو ملف المفتاح الذي تم ضبط المشروع مسبقاً للتوقيع به. وينبغي أن تظهر لك الرسالة **Created the strong-name key**.

1. في برنامج Visual Studio، اختر **File** > **Open** > **Project/Solution**، وافتح ملف المشروع `AB400.Lab01.csproj`.

1. في نافذة **Solution Explorer**، افتح الملف `RequestApprovalPlugin.cs`. راجع كتلة التعليقات الموجودة أعلى الفئة — فهي توثق بدقة كيف ستقوم بتسجيل هذا الـ Plug-in في المهمة التالية: الرسالة `Update` على الجدول `eqp_request`، في مرحلة `PreOperation`، بالوضع المتزامن (Synchronous)، مع التصفية على العمود `eqp_requeststatus`، ومع صورة قبلية (Pre-image) باسم `PreImage` تحمل العمودين `eqp_requeststatus` و`eqp_currentdevice`.

1. ابحث عن التعليق **Confirm the request is being approved (read the Target and the pre-image)** وأضف الكود التالي تحته:

    ```csharp
    // Confirm the request is being approved (read the Target and the pre-image)
    var target = (Entity)context.InputParameters["Target"];
    if (!target.Attributes.Contains("eqp_requeststatus"))
    {
        return;
    }

    var newStatus = ((OptionSetValue)target["eqp_requeststatus"]).Value;
    if (newStatus != StatusApproved)
    {
        return;
    }

    var preImage = context.PreEntityImages["PreImage"];
    var previousStatus = ((OptionSetValue)preImage["eqp_requeststatus"]).Value;
    if (previousStatus == StatusApproved)
    {
        return;
    }
    ```

    يحمل الكائن `Target` فقط الأعمدة المضمنة في عملية التحديث الجارية — وهنا يحمل فقط القيمة الجديدة للعمود `eqp_requeststatus` لأنه هو عمود التصفية (Filtering attribute). بينما تحمل الصورة القبلية (Pre-image) قيم السجل *قبل* التحديث، ولذلك فإن مقارنة `previousStatus` بالقيمة الجديدة هي الطريقة الدقيقة التي يكتشف بها الـ Plug-in حدوث انتقال فعلي إلى حالة الاعتماد (Approved)، بدلاً من عملية حفظ عادية تترك طلباً معتمداً مسبقاً دون تغيير في حالته.

1. ابحث عن التعليق **Retrieve the device being replaced** وأضف الكود التالي:

    ```csharp
    // Retrieve the device being replaced
    var deviceRef = preImage.GetAttributeValue<EntityReference>("eqp_currentdevice");

    Entity device;
    try
    {
        device = service.Retrieve("eqp_device", deviceRef.Id, new ColumnSet("eqp_issuedon", "eqp_damagedbeyondrepair"));
    }
    catch (FaultException<OrganizationServiceFault>)
    {
        throw new InvalidPluginExecutionException("The device being replaced couldn't be found.");
    }
    ```

    بما أن العمود `eqp_currentdevice` ليس جزءاً من عملية التحديث الحالية، يتم جلبه أيضاً من الصورة القبلية (Pre-image). ويقرأ استدعاء `IOrganizationService.Retrieve` العمودين اللذين تحتاجهما القاعدة فقط عبر ColumnSet — وهما تاريخ الإصدار وعلامة التلف غير القابل للإصلاح.

1. ابحث عن التعليق **Apply the replacement-eligibility rule** وأضف الكود التالي:

    ```csharp
    // Apply the replacement-eligibility rule
    var issuedOn = device.GetAttributeValue<DateTime?>("eqp_issuedon");
    var damagedBeyondRepair = device.GetAttributeValue<bool>("eqp_damagedbeyondrepair");

    var isEligible = damagedBeyondRepair
        || !issuedOn.HasValue
        || issuedOn.Value.Date <= DateTime.UtcNow.Date.AddMonths(-24);
    ```

    هذه هي قاعدة العمل الأساسية: يكون الجهاز مؤهلاً للاستبدال إذا كان مميزاً بأنه تالف وغير قابل للإصلاح، أو إذا لم يكن له تاريخ إصدار مسجل، أو إذا كان قد تم إصداره في أو قبل تاريخ اليوم (بتوقيت UTC) مطروحاً منه 24 شهراً تقويمياً.

1. ابحث عن التعليق **Block the approval if the device isn't eligible** وأضف الكود التالي:

    ```csharp
    // Block the approval if the device isn't eligible
    if (!isEligible)
    {
        var eligibleFrom = issuedOn.Value.Date.AddMonths(24);
        throw new InvalidPluginExecutionException(
            $"This device was issued on {issuedOn.Value:yyyy-MM-dd}. It can be replaced from {eligibleFrom:yyyy-MM-dd}, or earlier if it's flagged as damaged beyond repair.");
    }
    ```

    إن رمي الاستثناء `InvalidPluginExecutionException` داخل خطوة متزامنة (Synchronous) في مرحلة PreOperation يوقف عملية التحديث قبل أن يعتمدها Dataverse في قاعدة البيانات. ويتلقى المستدعي — سواء كان نموذج المتصفح أو استدعاء Web API المباشر كما ستجرب بعد قليل — نص هذه الرسالة كرسالة خطأ رسمية.

1. اختر **Build** > **Build Solution** (أو اضغط **Ctrl+Shift+B**) وتأكد من نجاح بناء المشروع بدون أي أخطاء.

## تسجيل الـ Plug-in باستخدام أداة Plug-in Registration Tool

بعد ترجمة الكود وبناء ملف التجميع، تحتاج الآن إلى إخبار Dataverse بتشغيله — وتحديد التوقيت الدقيق لتشغيله. ستقوم بتسجيل التجميع (Assembly)، ثم تسجيل خطوة (Step) على رسالة `Update` الخاصة بالجدول `eqp_request`، ثم تسجيل صورة قبلية (Pre-image) تقرأ منها الخطوة.

1. افتح نافذة الطرفية وشغّل أداة Plugin Registration Tool:

    ```powershell
    pac tool prt
    ```

1. اختر **+ Create new connection**، وحدد الخيار **Display list of available organizations**، ثم سجّل الدخول ببيانات اعتمادك واتصل ببيئة Dataverse التي تستخدمها في هذا التمرين.

1. من قائمة **Register**، اختر **New Assembly**.

1. في نافذة **Register New Assembly**، اضغط على زر النقاط الثلاث (**…**) واستعرض للوصول إلى الملف `AB400.Lab01.dll` داخل مجلد المشروع `bin\Debug\net48`. تأكد من ضبط **Isolation Mode** على **Sandbox** وضبط **Location** على **Database**، ثم اضغط **Register Selected Plugins**.

1. قم بتوسيع العقده **(Assembly) AB400.Lab01**، وانقر بزر الماوس الأيمن على **(Plugin) AB400.Lab01.RequestApprovalPlugin**، واختر **Register New Step**.

1. في نافذة **Register New Step**، اضبط القيم التالية:

    | الإعداد (Setting) | القيمة (Value) |
    |:--|:--|
    | Message | `Update` |
    | Primary Entity | `eqp_request` |
    | Filtering Attributes | `eqp_requeststatus` فقط |
    | Event Pipeline Stage of Execution | **PreOperation** |
    | Execution Mode | **Synchronous** |
    | Description | *Lab 01: enforce replacement eligibility on approval* |

    افتح محدد **Filtering Attributes** واختر العمود `eqp_requeststatus` فقط — لا تقم بتضمين المفتاح الأساسي (Primary key)، ولا تحدد جميع الأعمدة. ثم اضغط **Register New Step**.

    > **Note**: إذا أظهرت أداة Plugin Registration Tool الخطأ التالي بعد النقر على **Register New Step**، فقد تكون الخطوة قد حُفظت بالفعل قبل أن تفشل الأداة في تحديث واجهة العرض. لا تفترض نجاح التسجيل دون تحقق:
    >
    > ```output
    > Unhandled Exception: System.NullReferenceException: Object reference not set to an instance of an object.
    >    at Microsoft.Crm.Tools.Libraries.OrganizationHelper.GetColumnSet(String entityName, CrmOrganization org)
    >    at Microsoft.Crm.Tools.Libraries.OrganizationHelper.RefreshStep(CrmOrganization org, CrmPluginStep step)
    >    at Microsoft.Crm.Tools.PluginRegistration.StepRegistrationViewModel.RegisterStep(Object sender, EventArgs e)
    > ```
    >
    > تحقق من التسجيل المحفوظ قبل المتابعة:
    >
    > 1. اضغط **Cancel** لإغلاق نافذة التسجيل.
    > 1. قم بتوسيع التجميع وفئة الـ Plug-in. تأكد من وجود الخطوة، ثم افتح خصائصها وتحقق من تطابق **Message** و**Primary Entity** و**Filtering Attributes** و**Event Pipeline Stage of Execution** و**Execution Mode** مع الجدول أعلاه.
    >
    > إذا لم تكن الخطوة موجودة أو كانت إعداداتها غير مطابقة، فتوقف وقم بحل مشكلة التسجيل قبل إضافة الصورة أو اختبار الـ Plug-in. لا تتجاهل الأخطاء الأخرى ولا تنشئ خطوة مكررة.

1. انقر بزر الماوس الأيمن على الخطوة التي سجلتها للتو، واختر **Register New Image**.

1. في نافذة **Register New Image**، اضبط الإعدادات التالية:

    | الإعداد (Setting) | القيمة (Value) |
    |:--|:--|
    | Image Type | **Pre Image** |
    | Name | `PreImage` |
    | Entity Alias | `PreImage` |
    | Parameters | `eqp_requeststatus`, `eqp_currentdevice` فقط |

    يجب أن يكون الاسم المستعار للكيان (**Entity Alias**) مطابقاً تماماً للنص `PreImage` — فهو المفتاح النصي الذي يستخدمه الكود لقراءة `context.PreEntityImages["PreImage"]`. حدد فقط العمودين اللذين يقرؤهما الـ Plug-in؛ فتسجيل جميع الأعمدة في الصورة يُعد خطأً شائعاً ومكلفاً للأداء يمكن تجنبه بسهولة. اضغط **Register New Image** (أو **Save**) للإنهاء.

   ينبغي أن ترى الخطوة الجديدة ومعها صورتها القبلية مدرجة تحت **(Plugin) AB400.Lab01.RequestApprovalPlugin** في أداة Plugin Registration Tool.

## إعادة ضبط بيانات المعمل والتأكد من منع الـ Plug-in لمحاولة التجاوز

الآن أعد تنفيذ نفس محاولة التجاوز التي قمت بها في بداية التمرين، ولكن مع وجود الـ Plug-in مسجلاً وفعالاً على الخادم.

1. بالعودة إلى تطبيق **Equipment Provisioning**، وفي شريط الأوامر الخاص بطريقة العرض **Active Requests**، اختر **Reset lab data**. يؤدي ذلك إلى استعادة حالة السجل `REQ-SEED-001` إلى **Submitted**، ملغياً الاعتماد السابق الناتج عن تجاوز Web API.

1. في نافذة الطرفية، شغّل سكربت التجاوز مرة أخرى لنفس الطلب:

    ```powershell
    .\Approve-RequestViaWebApi.ps1 -EnvironmentUrl "<your environment URL>" -RequestNumber "REQ-SEED-001"
    ```

   في هذه المرة سيفشل السكربت، وينبغي أن تظهر لك رسالة خطأ مشابهة لما يلي:

    ```output
    The Web API rejected the request for REQ-SEED-001. ... This device was issued on 2024-02-01. It can be replaced from 2026-02-01, or earlier if it's flagged as damaged beyond repair. ...
    ```

   قم بتحديث (Refresh) السجل `REQ-SEED-001` داخل التطبيق وتأكد من أن **Request status** لا يزال على الحالة **Submitted**. إن نفس الاستدعاء الذي نجح في بداية التمرين يتم إيقافه الآن على الخادم (Server) — حيث لم يكن بإمكان أي فحص على جانب العميل إيقافه أبداً.

1. الآن شغّل نفس السكربت للطلب `REQ-SEED-002`، وهو طلب خاص بجهاز مميز بأنه تالف وغير قابل للإصلاح:

    ```powershell
    .\Approve-RequestViaWebApi.ps1 -EnvironmentUrl "<your environment URL>" -RequestNumber "REQ-SEED-002"
    ```

   في هذه المرة ينجح التنفيذ. قم بتحديث `REQ-SEED-002` في التطبيق وتأكد من أن **Request status** أصبح الآن **Approved**.

   هذا الاختبار الثاني لا يقل أهمية عن الاختبار الأول؛ فلو كان الـ Plug-in يرفض كل عمليات الاعتماد عشوائياً لاجتاز الاختبار الأول أيضاً! إن نجاح اعتماد `REQ-SEED-002` يثبت أن الـ Plug-in الخاص بك يطبق قاعدة العمل بانتقائية ودقة، وليس كحظر شامل.

## فهرسة قاعدة الأهلية كحدث أعمال (Catalog the eligibility rule as a business event)

إن نفس منطق التحقق من أهلية الاستبدال الذي قمت بتنفيذه للتو متاح أيضاً كواجهة برمجية مخصصة (Custom API) في Dataverse باسم `eqp_IsEligibleForReplacement` مرفقة مع الحل الأساسي. ولكي تجعلها قابلة للاكتشاف بواسطة Power Automate والمشتركين الآخرين، ستقوم بفهرستها كحدث أعمال (Business event) في Dataverse باستخدام جدولي `Catalog` و`CatalogAssignment`.

1. في بوابة الصانع، اختر **Solutions**، ثم اختر **+ New solution** (أو افتحه إذا كنت قد أنشأته مسبقاً في هذا التمرين). أطلق عليه الاسم `AB400 Lab 01 catalog`، واختر ناشراً (Publisher)، ثم اضغط **Create**.

1. داخل الحل الجديد، اختر **New**، ثم اختر **Catalog**. (إذا لم يكن الخيار **Catalog** ظاهراً مباشرة، فاختر **More** أولاً).

1. أنشئ الدليل الجذر (Root catalog) لهذا الحل بالقيم التالية:

    | الحقل (Field) | القيمة (Value) |
    |:--|:--|
    | Parent Catalog | *اتركه فارغاً* |
    | Name | `AB400 Lab 01` |
    | Display Name | `AB400 Lab 01` |
    | Description | `Business events cataloged for AB-400 Lab 01.` |

    أثناء كتابتك في حقل **Name**، يتم ملء الحقل **Unique Name** تلقائياً باستخدام بادئة الناشر — ويمكنك ترك القيمة المولدة كما هي. احفظ النموذج وأغلقه.

1. اختر **New** > **Catalog** مرة أخرى لإنشاء دليل المستوى الثاني (الفئة التصنيفية Category):

    | الحقل (Field) | القيمة (Value) |
    |:--|:--|
    | Parent Catalog | `AB400 Lab 01` (الدليل الجذر الذي أنشأته للتو) |
    | Name | `Equipment eligibility` |
    | Display Name | `Equipment eligibility` |
    | Description | `Business events related to equipment replacement eligibility.` |

    احفظ النموذج وأغلقه.

1. اختر علامة التبويب **Catalog Assignment**، ثم اختر **New Catalog Assignment**. أدخل `eqp_IsEligibleForReplacement` في حقل **Name**، واضبط **Catalog Assignment Object** على الـ Custom API المسماة `eqp_IsEligibleForReplacement` (ابحث عنها بالاسم)، واضبط الدليل على فئة **Equipment eligibility** التي أنشأتها للتو. احفظ النموذج وأغلقه.

1. تحقق الآن من أن حدث الأعمال أصبح قابلاً للاكتشاف: افتح بوابة [Power Automate](https://make.powerautomate.com){:target="_blank"} على الرابط `https://make.powerautomate.com`، وتأكد من أن محدد البيئة (في الأعلى يميناً) يعرض نفس البيئة التي كنت تستخدمها.

1. اختر **Create**، ثم اختر **Automated cloud flow**. امنحه أي اسم — على سبيل المثال، `AB400 Lab 01 flow check - don't save` — وابحث عن **Dataverse**، واختر المشغل (Trigger) المسمى **When an action is performed**، ثم اضغط **Create**.

1. في إعدادات المشغل، اضبط **Catalog** على `AB400 Lab 01`، واضبط **Category** على `Equipment eligibility`، واضبط **Table name** على **(none)**.

   ينبغي أن ترى العملية `eqp_IsEligibleForReplacement` مدرجة في قائمة **Action name** — مما يثبت أن نفس القاعدة التي نفذتها كـ Plug-in أصبحت الآن مفهرسة وقابلة للاكتشاف والاستخدام بواسطة أي Cloud Flow في البيئة.

1. أغلق التدفق **دون حفظه**. يهدف هذا التمرين فقط إلى إثبات قابلية اكتشاف الحدث، وليس بناء تدفق يستهلكه.

## تنظيف البيئة (Clean up)

إذا انتهيت من الاستكشاف والتجربة، فقم بإزالة ما سجلته وأنشأته في هذا التمرين. إن ترك هذه المكونات لا يعطل أي تمرين آخر، ولكن إزالتها يحافظ على نظافة بيئتك التطويرية.

1. افتح أداة Plugin Registration Tool (`pac tool prt`) واتصل ببيئتك.

1. قم بتوسيع **(Assembly) AB400.Lab01** > **(Plugin) AB400.Lab01.RequestApprovalPlugin**، وانقر بزر الماوس الأيمن على الخطوة المسجلة واختر **Unregister**. تأكد من إزالة الصورة القبلية (Pre-image) معها.

1. انقر بزر الماوس الأيمن على **(Assembly) AB400.Lab01** واختر **Unregister** لإزالة ملف التجميع بالكامل.

1. في بوابة الصانع، افتح الحل **AB400 Lab 01 catalog** واحذف المكونات التي أنشأتها بهذا الترتيب الدقيق: أولاً **Catalog Assignment**، ثم فئة **Equipment eligibility**، وأخيراً الدليل الجذر **AB400 Lab 01**.

1. في صفحة **Solutions**، حدد الحل **EquipmentProvisioningLab01** واختر **Delete** لإلغاء تثبيته. يزيل ذلك نموذج **Request intake** وفحص جانب العميل الخاص به، ولا يؤثر على الحل الأساسي **Equipment Provisioning (base)**.

## الملخص (Summary)

في هذا التمرين العملي، تحققت بنفسك من أن فحص جانب العميل على نموذج Dataverse يمكن تجاوزه عبر واجهة Web API، ثم أغلقت تلك الثغرة نهائياً باستخدام Plug-in على جانب الخادم. واستخدمت صورة قبلية (Pre-image) لرصد انتقال حالة الاعتماد، وخدمة المؤسسة (Organization service) للاستعلام عن بيانات الجهاز المرتبط، وأداة Plugin Registration Tool لتسجيل خطوة متزامنة في مرحلة PreOperation مع خصائص التصفية (Filtering Attributes) وصورة الكيان. كما تحققت من أن الـ Plug-in يفرض القاعدة بانتقائية — حيث يمنع الاعتماد غير المؤهل بينما يسمح بالاستثناء المشروع — وقمت بفهرسة الـ Custom API الخاصة بنفس القاعدة كحدث أعمال في Dataverse لكي تتمكن مسارات الأتمتة الأخرى من اكتشافه.

لقد أكملت هذا التمرين بنجاح.

<!-- study-aid-answer-key-start -->
## ملحق الكود المرجعي الكامل للمعمل وشرحه التفصيلي (`Build/LabReference/01-equipment-validation-plugin`)

يوفر المستودع الرسمي للدورة النسخة المرجعية المكتملة للحل في الملف المحلي `book/labs-code/Build/LabReference/01-equipment-validation-plugin/AB400.Lab01/RequestApprovalPlugin.cs`. فيما يلي الكود المصدري الكامل للملف المرجعي (84 سطراً كاملاً دون حذف) متبوعاً بالتحليل الهندسي التفصيلي لكل جزء منه:

```csharp
using System;
using System.ServiceModel;
using Microsoft.Xrm.Sdk;
using Microsoft.Xrm.Sdk.Query;

namespace AB400.Lab01
{
    // Completed reference for Lab 01. Enforces R1 (replacement eligibility, foundation
    // spec §3) when a request's status changes to Approved.
    //
    // Registration (Plug-in Registration Tool):
    //   Message:              Update
    //   Primary Entity:       eqp_request
    //   Event Pipeline Stage: PreOperation
    //   Execution Mode:       Synchronous
    //   Filtering Attributes: eqp_requeststatus
    //   Pre-image ("PreImage"): eqp_requeststatus, eqp_currentdevice
    public class RequestApprovalPlugin : IPlugin
    {
        private const int StatusApproved = 100000001;

        public void Execute(IServiceProvider serviceProvider)
        {
            // Get the execution context and organization service
            var context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
            var factory = (IOrganizationServiceFactory)serviceProvider.GetService(typeof(IOrganizationServiceFactory));
            var service = factory.CreateOrganizationService(context.UserId);

            // Confirm the request is being approved (read the Target and the pre-image)
            var target = (Entity)context.InputParameters["Target"];
            if (!target.Attributes.Contains("eqp_requeststatus"))
            {
                // The filtering attribute guarantees this never happens in practice, but
                // guard against being invoked for an unrelated update.
                return;
            }

            var newStatus = ((OptionSetValue)target["eqp_requeststatus"]).Value;
            if (newStatus != StatusApproved)
            {
                // Some other status transition (for example, to Rejected). R1 only applies to approval.
                return;
            }

            var preImage = context.PreEntityImages["PreImage"];
            var previousStatus = ((OptionSetValue)preImage["eqp_requeststatus"]).Value;
            if (previousStatus == StatusApproved)
            {
                // The request was already Approved; this save didn't change the status,
                // so there's no new approval transition to validate.
                return;
            }

            // Retrieve the device being replaced
            var deviceRef = preImage.GetAttributeValue<EntityReference>("eqp_currentdevice");

            Entity device;
            try
            {
                device = service.Retrieve("eqp_device", deviceRef.Id, new ColumnSet("eqp_issuedon", "eqp_damagedbeyondrepair"));
            }
            catch (FaultException<OrganizationServiceFault>)
            {
                throw new InvalidPluginExecutionException("The device being replaced couldn't be found.");
            }

            var issuedOn = device.GetAttributeValue<DateTime?>("eqp_issuedon");
            var damagedBeyondRepair = device.GetAttributeValue<bool>("eqp_damagedbeyondrepair");

            // Apply the replacement-eligibility rule
            var isEligible = damagedBeyondRepair
                || !issuedOn.HasValue
                || issuedOn.Value.Date <= DateTime.UtcNow.Date.AddMonths(-24);

            // Block the approval if the device isn't eligible
            if (!isEligible)
            {
                var eligibleFrom = issuedOn.Value.Date.AddMonths(24);
                throw new InvalidPluginExecutionException(
                    $"This device was issued on {issuedOn.Value:yyyy-MM-dd}. It can be replaced from {eligibleFrom:yyyy-MM-dd}, or earlier if it's flagged as damaged beyond repair.");
            }
        }
    }
}
```

### التحليل الهندسي التفصيلي للكود المرجعي (سطراً بسطر):

1. **الأسطر `20–27` (التصميم عديم الحالة `Stateless` واستخراج الخدمات):**
   - يُعرَّف `StatusApproved = 100000001` كـ `const int` ثابت لا يتغير بين الاستدعاءات، بينما يتم استخراج `context` و`factory` و`service` محلياً داخل `Execute(IServiceProvider serviceProvider)` لضمان الأمان التام عند تخزين النسخة مؤقتاً (`Caching`) بواسطة `Dataverse`.
2. **الأسطر `30–52` (التحقق الثلاثي من تحوّل الحالة `State Transition Guard`):**
   - **الحارس الأول (`!target.Attributes.Contains("eqp_requeststatus")`):** دفاع وقائي في حال تم تعديل `Filtering Attributes` مستقبلاً بالخطأ.
   - **الحارس الثاني (`newStatus != StatusApproved`):** يتأكد من أن القيمة الجديدة هي الاعتماد (`100000001`) وليست حالة أخرى مثل الرفض (`Rejected`).
   - **الحارس الثالث (`previousStatus == StatusApproved`):** يقرأ القيمة القديمة من `context.PreEntityImages["PreImage"]` للتأكد من أن السجل لم يكن معتمداً مسبقاً قبل هذا التحديث.
3. **الأسطر `55–65` (قراءة المرجع `EntityReference` والاستعلام المقتصد عبر `ColumnSet`):**
   - يستخرج `eqp_currentdevice` من `preImage` لأن المستخدم عندما يغير حقل الحالة فقط لا يرسل حقل الجهاز ضمن `Target`.
   - يستدعي `service.Retrieve` مع تمرير `new ColumnSet("eqp_issuedon", "eqp_damagedbeyondrepair")` لجلب العمودين المطلوبين فقط، ويحوّل أي `FaultException<OrganizationServiceFault>` إلى `InvalidPluginExecutionException` برسالة واضحة للمستخدم.
4. **الأسطر `67–81` (حساب الأهلية بتوقيت `UTC` وإجهاض المعاملة):**
   - يستخدم `GetAttributeValue<DateTime?>` و`GetAttributeValue<bool>` اللذين يعيدان القيمة الافتراضية بأمان (`null` أو `false`) دون رمي `KeyNotFoundException` إذا كان العمود فارغاً في قاعدة البيانات.
   - عند عدم تحقق الشرط `isEligible`، يرمي `InvalidPluginExecutionException` في مرحلة `PreOperation` فيلغي التحديث فوراً سواء جاء من نموذج المتصفح أو من `Dataverse Web API`.
<!-- study-aid-answer-key-end -->