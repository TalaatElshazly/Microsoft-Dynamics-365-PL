# معمل 00: إعداد بيئة التطوير وأدوات سطر الأوامر (PAC CLI)
## Lab 00: Environment Setup, PAC CLI, and Developer Workstation Configuration

هذا المعمل هو الخطوة الأولى التأسيسية (Milestone 0) لتهيئة محطة عمل مطور **Microsoft Power Platform & Dataverse** المنطلق من خلفية **.NET / C#**.

---

## 1. أهداف المعمل (Lab Objectives)
1. إنشاء وتفعيل بيئة مطور مجانية كاملة الميزات عبر **Power Apps Developer Plan**.
2. تثبيت وضبط أداة سطر أوامر المنصة الرسمية **PAC CLI (Power Platform CLI)**.
3. إنشاء ملف مصادقة محلي آمن وربط محطة العمل ببيئة Dataverse السحابية.
4. إنشاء ناشر حلول مخصص (`Solution Publisher`) بالبادئة المعتمدة `ep_`.
5. تهيئة أول مشروع حل Dataverse مؤسسي عبر سطر الأوامر وتجهيزه للمستودع.

---

## 2. متطلبات بيئة العمل (Prerequisites)
- نظام تشغيل Windows 10/11 x64.
- مثبت .NET SDK (الإصدار .NET 8 أو أحدث؛ تم التحقق من توفر SDK في الجهاز).
- بيئة Visual Studio 2022 (Community أو Professional) مع حزم العمل:
  - *.NET Desktop Development*
  - *ASP.NET and Web Development*
- حساب Microsoft شخصي أو مؤسسي للاشتراك في Developer Plan.

---

## 3. خطوات التنفيذ التفصيلية (Step-by-Step Execution)

### الخطوة 1: الاشتراك في Power Apps Developer Plan
1. توجه إلى الرابط الرسمي: [Power Apps Developer Plan](https://powerapps.microsoft.com/developerplan/).
2. اضغط على **Get started free** وسجل الدخول بحسابك.
3. عند اكتمال التسجيل، سيتم توفير بيئة مطور مخصصة لك (`Developer Environment`) تتضمن قاعدة بيانات **Microsoft Dataverse** كاملة الصلاحيات مع صلاحيات مدير النظام (`System Administrator`).
4. انسخ رابط البيئة (Instance URL) من شريط العنوان أو من مركز الإدارة [Power Platform Admin Center](https://admin.powerplatform.microsoft.com):
   - مثال: `https://orgXXXXX.crm.dynamics.com`

---

### الخطوة 2: تثبيت وتفعيل أداة PAC CLI
بصفتك مطور .NET، الطريقة الأسرع والموصى بها لتثبيت أداة PAC CLI هي عبر `dotnet tool`:

```powershell
# تثبيت PAC CLI كأداة عامة على مستوى الجهاز
dotnet tool install --global Microsoft.PowerApps.CLI.Tool

# في حال كانت مثبتة مسبقاً، يمكنك ترقيتها لأحدث إصدار عبر:
dotnet tool update --global Microsoft.PowerApps.CLI.Tool

# التحقق من نجاح التثبيت وعرض الإصدار:
pac --version
```

> [!TIP]
> إذا كنت تفضل استخدام ملحقات Visual Studio Code، يمكنك البحث عن ملحق **Power Platform Tools** وتثبيته مباشرة، وسيتكفل تلقائياً بإتاحة أمر `pac` داخل الطرفية المدمجة.

---

### الخطوة 3: إنشاء ملف المصادقة والاتصال بالبيئة (Authentication Profiles)
قم بإنشاء بروفايل مصادقة محلي للاتصال ببيئة Dataverse السحابية الخاصة بك:

```powershell
# إنشاء ملف مصادقة وفتح نافذة تسجيل الدخول في المتصفح
pac auth create --name "DevEnv" --url "https://orgXXXXX.crm.dynamics.com"

# عرض قائمة ملفات المصادقة المتاحة والتحقق من البيئة النشطة
pac auth list

# عرض تفاصيل المنظمة النشطة حالياً
pac org who
```

---

### الخطوة 4: إنشاء ناشر الحلول المخصص (Solution Publisher)
في بيئات العمل الاحترافية، لا نستخدم الناشر الافتراضي (`Default Publisher` بالبادئة `new_` أو `crXXX_`). نقوم بإنشاء ناشر مؤسسي رسمي:

1. افتح بوابة صانع الحلول [make.powerapps.com](https://make.powerapps.com) وتأكد من اختيار بيئة المطور الخاصة بك من الزاوية العلوية.
2. انتقل إلى **Solutions** -> علامة تبويب **Publishers** -> اضغط **New publisher**.
3. أدخل البيانات التالية بدقة:
   - **Display name**: `Equipment Provisioning Publisher`
   - **Name**: `ep_publisher`
   - **Prefix**: `ep` (هذه البادئة ستسبق تلقائياً جميع الجداول والأعمدة مثل `ep_device`)
   - **Choice value prefix**: `10000` (تضمن تفرد أرقام الخيارات عبر البيئات)
4. اضغط **Save**.

---

### الخطوة 5: تهيئة مشروع الحل الأول عبر PAC CLI
داخل بيئة العمل في المجلد المخصص لحلول Dataverse، ننشئ بنية الحل:

```powershell
# الانتقال إلى مجلد حلول Dataverse في مشروع المحفظة
cd "e:\Microsoft Dynamics\portfolio\equipment-provisioning\dataverse"

# تهيئة حل Dataverse جديد
pac solution init --publisher-name "ep_publisher" --publisher-prefix "ep"

# فحص الملفات الناتجة (cdsproj, Solution.xml, Other/Solution.xml)
dir
```

---

## 4. قائمة التحقق من الإنجاز ومعايير القبول (Acceptance Criteria)

- [ ] تم إنشاء بيئة المطور بنجاح وظهور قاعدة بيانات Dataverse.
- [ ] الأمر `pac --version` يعمل بنجاح ويعرض رقم الإصدار.
- [ ] الأمر `pac auth list` يعرض الاتصال بحالة نشطة (`*`).
- [ ] تم إنشاء الناشر بالبادئة `ep` وقيمة الخيارات `10000`.
- [ ] مجلد `dataverse/` يحتوي على ملف مشروع الحل `cdsproj` مهيأ بالبادئة `ep`.
