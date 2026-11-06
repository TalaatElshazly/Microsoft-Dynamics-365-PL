# المعمارية الشاملة لنظام إدارة وتخصيص المعدات
## Enterprise System Architecture & Component Interaction

توضح هذه الوثيقة المعمارية الفنية الشاملة لنظام **Equipment Provisioning & Asset Lifecycle Management System**، موضحة حدود التنفيذ (`Execution Boundaries`)، تدفق البيانات، ونموذج الأمان والتكامل بين مكونات المنصة السحابية وتقنيات **.NET / C#** و **Azure**.

---

## 1. مخطط المكونات وحدود المعالجة (Component Interaction Diagram)

```mermaid
flowchart TD
    subgraph UI_Client["واجهة المستخدم وبرمجة العميل (Client Tier)"]
        MDA["تطبيق مبني على نموذج (Model-Driven App)"]
        PCF["عنصر تحكم تفاعلي (PCF React Component)"]
        TS["سكربت العميل (TypeScript / FormContext)"]
        COPILOT["مساعد Copilot التفاعلي (Copilot Studio Agent)"]
    end

    subgraph Dataverse_Core["بيئة المعالجة المركزية (Dataverse Platform Tier)"]
        API["واجهة OData v4 Web API"]
        SEC["نموذج الأمان ووحدات الأعمال (RBAC & Business Units)"]
        
        subgraph Pipeline["مسار معالجة الأحداث (Event Execution Pipeline)"]
            STAGE10["المرحلة 10: Pre-Validation (التحقق من الأهلية)"]
            STAGE20["المرحلة 20: Pre-Operation (تخصيص الكيان وحساب القيم)"]
            DB[(قاعدة بيانات SQL Azure المركزية)]
            STAGE40["المرحلة 40: Post-Operation (تسجيل الحركات والربط)"]
        end
        
        CUSTOM_API["الواجهات المخصصة (Custom APIs)"]
    end

    subgraph Azure_Cloud["خدمات السحابة والتكامل (Microsoft Azure Tier)"]
        SB["ناقل الخدمة (Azure Service Bus Queue / Topic)"]
        AF["دالة سحابية (Azure Function - C# Isolated Worker)"]
        KV["خزنة المفاتيح (Azure Key Vault)"]
    end

    subgraph External_Tiers["الأنظمة الخارجية وإدارة الأصول (External Tier)"]
        DOTNET_DAEMON[".NET 8 Asset Sync Daemon Service"]
        ERP_DB[("نظام إدارة الأصول المركزي (ERP / SAP)")]
    end

    %% التدفقات والروابط
    MDA --> TS
    MDA --> PCF
    TS --> API
    PCF --> API
    COPILOT --> API
    
    API --> SEC
    SEC --> STAGE10
    STAGE10 --> STAGE20
    STAGE20 --> DB
    DB --> STAGE40
    
    STAGE40 -.->|"استدعاء غير متزامن (Service Endpoint)"| SB
    STAGE40 -.->|"خطاف الويب (Webhook)"| AF
    
    SB --> AF
    AF -->|"استعلامات وتحديث الحالة"| API
    AF --- KV
    
    DOTNET_DAEMON -->|"مزامنة مجمعة (ServiceClient / $batch)"| API
    DOTNET_DAEMON <--> ERP_DB
```

---

## 2. حدود التنفيذ والبيئات المعزولة (Execution Boundaries)

### 1. بيئة المتصفح والعميل (Client Browser Boundary)
- **التقنيات**: TypeScript, React, Fluent UI v9, Dataverse Web API Client.
- **طبيعة المعالجة**: معالجة تفاعلية غير موثوقة أمنياً من جانب الخادم (`Untrusted Environment`).
- **المسؤولية**:
  - التحسين البصري لتجربة المستخدم (UI/UX).
  - التحقق المبدئي السريع من المدخلات لتقليل زمن الاستجابة.
  - لا يُعتمد عليها في فرض القيود المالية، الأمنية، أو التحقق من توفر المخزون الحرج.

### 2. بيئة المنصة المركزية وحاوية الخادم (Dataverse Execution Sandbox Boundary)
- **التقنيات**: C# (.NET Framework 4.6.2 / Dataverse Isolation Mode: Sandbox).
- **طبيعة المعالجة**: بيئة خادم مؤمنة ومعزولة تديرها مايكروسوفت جزئياً وتفرض حدوداً صارمة على الموارد:
  - أقصى مدة لتنفيذ الإضافة المتزامنة: **دقيقتان (120 ثانية)**.
  - منع الوصول المباشر لنظام الملفات، وسجل النظام (Registry)، أو منافذ الشبكة المحلية.
  - الاتصال الشبكي مسموح فقط عبر بروتوكولات HTTPS على المنافذ القياسية (443/80).
- **المسؤولية**:
  - فرض قواعد العمل الإلزامية التي لا يمكن تجاوزها حتى لو استُدعيت البيانات عبر واجهات برمجية خارجية.
  - ضمان سلامة المعاملة المتزامنة (`ACID Transaction Boundary`). إذا فشل تخصيص الجهاز أو تبين نفاذ المخزون، يتم التراجع عن كافة عمليات الحفظ (`Rollback`).

### 3. بيئة المعالجة السحابية الخلفية (Azure Isolated Serverless Boundary)
- **التقنيات**: .NET 8 (Isolated Worker Process), Azure Functions, Azure Service Bus.
- **طبيعة المعالجة**: خوادم حوسبة مرنة غير مقيدة بمهلة الـ 120 ثانية الخاصة بـ Dataverse Sandbox.
- **المسؤولية**:
  - المهام طويلة المدى (تجهيز أنظمة التشغيل، تفعيل تراخيص البرامج، إرسال خطابات العهدة الرسمية).
  - استهلاك الرسائل بنمط النشر والاشتراك (`Publish-Subscribe`) عبر Azure Service Bus.
  - إيقاف تشغيل ومحاولة إعادة إرسال الرسائل الفاشلة تلقائياً عبر طابور الرسائل التالفة (`Dead-Letter Queue`).

### 4. بيئة خدمات المزامنة الخلفية (.NET 8 Daemon Boundary)
- **التقنيات**: .NET 8 Background Worker Service, `Microsoft.PowerPlatform.Dataverse.Client` (`ServiceClient`).
- **طبيعة المعالجة**: تطبيق يعمل كخدمة بنظام Windows Service أو Linux Container داخل شبكة المؤسسة.
- **المسؤولية**:
  - مزامنة كشوفات الأجهزة المشتراة حديثاً من نظام الـ ERP إلى Dataverse.
  - استخدام طلبات الدفعات المجمعة (`ExecuteMultipleRequest` أو `$batch`) لتفادي تجاوز حدود طلبات API (`API Service Protection Limits`).

---

## 3. نموذج الأمان والمصادقة (Security & Identity Architecture)

```mermaid
sequenceDiagram
    autonumber
    actor Dev as مهندس النظام / العميل
    participant Entra as Microsoft Entra ID (Azure AD)
    participant Dataverse as Dataverse Web API & Sandbox
    participant AzureApp as Azure Function / Worker Service

    Note over Dev,Entra: 1. مصادقة المستخدم التفاعلية (User Interactive Auth)
    Dev->>Entra: طلب تسجيل الدخول (OAuth 2.0 Authorization Code Flow)
    Entra-->>Dev: إصدار Access Token يتضمن أدوار ومجموعات المستخدم

    Dev->>Dataverse: إرسال الطلب مع الترويسة Authorization: Bearer <Token>
    Dataverse->>Dataverse: فحص أدوار الأمان (Security Roles) ومجال وحدة الأعمال (BU)

    Note over AzureApp,Dataverse: 2. مصادقة الخدمات المؤتمتة (Service-to-Service S2S)
    AzureApp->>Entra: طلب توكن باستخدام Client Credentials Flow (App Secret / Certificate)
    Entra-->>AzureApp: إصدار Application Access Token
    AzureApp->>Dataverse: استدعاء Dataverse Web API باسم مستخدم التطبيق (Application User)
    Dataverse->>Dataverse: التحقق من صلاحيات مستخدم التطبيق المقترن بالـ App Registration
```

### معايير الأمان المطبقة:
1. **مستخدم التطبيق (Application User)**: الربط البرمجي بين Azure و Dataverse لا يستخدم حسابات مستخدمين شخصية إطلاقاً، بل يستخدم `Dataverse Application User` مقترناً بتسجيل تطبيق في Entra ID (`App Registration`) مع تطبيق مبدأ الصلاحيات الأدنى (`Least Privilege`).
2. **حماية أسرار النظام**: تُخزن شهادات وسلاسل الاتصال حصرياً داخل `Azure Key Vault` ولا يتم كتابة أي سر برمجي داخل مستودع الأكواد (`Zero Secret in Code`).
3. **أمان مستوى الحقول (Column-Level Security)**: حقول التكلفة المالية والأرقام التسلسلية الحساسة تخضع لملفات أمان الحقول (`Field Security Profiles`) لمنع ظهورها إلا للمستخدمين المصرح لهم.
