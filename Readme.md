# json_to_pdf  
# أداة json_to_pdf

A powerful Python utility to split and convert JSON data into well-formatted PDF documents.  
أداة بايثون قوية لتقسيم وتحويل بيانات JSON إلى مستندات PDF منسقة بشكل احترافي.

---

## 🚀 Project Description  
## 🚀 وصف المشروع

`json_to_pdf` streamlines the transformation of JSON files into multiple PDF documents.  
`json_to_pdf` تسهّل تحويل ملفات JSON إلى عدة مستندات PDF.

**Key benefits | المزايا الرئيسية:**

- **Intelligent Chunking:** Automatically divides arrays or objects into configurable segments.  
  **تقسيم ذكي:** تقسيم المصفوفات أو الكائنات تلقائيًا إلى أجزاء قابلة للتخصيص.
- **Creative Formatting:** Applies custom styles, headers, metadata tables, and adaptive layouts.  
  **تنسيق إبداعي:** تطبيق أنماط مخصصة، رؤوس، جداول بيانات وصفية، وتخطيطات متكيفة.
- **Parallel Processing:** Leverages multi-threading (with fallback to sequential mode) for large-scale conversions.  
  **المعالجة المتوازية:** استخدام المعالجة المتعددة (مع إمكانية الرجوع للوضع التسلسلي) لتحويلات البيانات الكبيرة.
- **Robust Error Handling:** Includes JSON repair heuristics, logging, and summary reports.  
  **معالجة أخطاء قوية:** تتضمن إصلاحات تلقائية، وتسجيل الأخطاء، وتقارير ملخصة.

**Implementation is encapsulated in three primary classes:**  
**التنفيذ مكوّن من ثلاث فئات رئيسية:**

- `JSONAnalyzer`: Parses and evaluates JSON structure, complexity, and creates content chunks.  
  تحليل بنية JSON وتقسيمها.
- `PDFGenerator`: Renders each chunk to a styled PDF using ReportLab.  
  توليد ملفات PDF من الأجزاء باستخدام مكتبة ReportLab.
- `JSONToPDFConverter`: Orchestrates loading, analysis, PDF generation, and summary reporting.  
  إدارة عملية التحويل بالكامل.

---

## 📦 Installation  
## 📦 التثبيت

### Prerequisites  
### المتطلبات المسبقة

- Python 3.7 or higher  
  بايثون 3.7 أو أحدث
- [ReportLab](https://pypi.org/project/reportlab/)  
  مكتبة ReportLab
- [tqdm](https://pypi.org/project/tqdm/) for progress bars  
  مكتبة tqdm لعرض تقدم العمليات

```bash
# Clone the repository
# استنساخ المستودع

git clone https://github.com/rayan-alharbi/json_to_pdf.git
cd json_to_pdf

# (Optional) Create a virtual environment
# (اختياري) إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate   # Windows

# Install required dependencies
# تثبيت المتطلبات
pip install reportlab tqdm

# (Optional) Install as a package
# (اختياري) تثبيت كحزمة
pip install .
```

---

## 🛠️ Usage Examples  
## 🛠️ أمثلة الاستخدام

### Basic CLI Usage  
### استخدام الأداة من الطرفية (CLI)

```bash
# Using default settings (40 PDF files)
# استخدام الإعدادات الافتراضية (40 ملف PDF)
json_to_pdf --input data.json

# Specify output directory and number of files
# تحديد مجلد الإخراج وعدد الملفات
json_to_pdf --input data.json --output ./pdfs --files 20
```

### Advanced CLI Options  
### خيارات متقدمة من الطرفية

```bash
json_to_pdf \
  --input large_dataset.json \
  --output ./reports \
  --files 50 \
  --sequential \
  --timeout 120 \
  --verbose
```

### Programmatic API  
### استخدام المكتبة برمجياً

```python
from json_to_pdf import JSONToPDFConverter

# Initialize converter
# تهيئة المحول
converter = JSONToPDFConverter(
    input_file="data.json",
    output_dir="./pdf_reports",
    num_files=30
)
converter.force_sequential = False  # or True for fallback
converter.timeout = 300            # seconds per PDF

# Run conversion
# تنفيذ التحويل
success = converter.convert()
if success:
    print("PDF generation completed successfully.")
else:
    print("Conversion encountered errors.")
```

---

## ⚙️ Configuration Options  
## ⚙️ خيارات الإعداد

| Parameter          | CLI Flag             | Default       | Description                                  | المعنى بالعربية                       |
| ------------------ | -------------------- | ------------- | -------------------------------------------- | -------------------------------------- |
| `input_file`       | `--input`, `-i`      | `test.json`   | Path to the source JSON file                 | مسار ملف JSON المصدر                  |
| `output_dir`       | `--output`, `-o`     | `output_pdfs` | Directory to save generated PDFs             | مجلد حفظ ملفات PDF الناتجة            |
| `num_files`        | `--files`, `-f`      | `40`          | Number of PDF chunks to produce              | عدد ملفات PDF المراد إنتاجها          |
| `force_sequential` | `--sequential`, `-s` | `False`       | Force sequential PDF generation              | فرض التحويل التسلسلي                  |
| `timeout`          | `--timeout`, `-t`    | `300`         | Timeout (in seconds) per PDF generation task | المهلة الزمنية (بالثواني) لكل ملف PDF  |
| `verbose`          | `--verbose`, `-v`    | `False`       | Enable detailed logging to console and file  | تفعيل السجلات التفصيلية               |

---

## 📖 API Documentation  
## 📖 توثيق الواجهة البرمجية

### `JSONAnalyzer(data)`

- **Parameters | المعاملات**:
  - `data` (`dict | list | any`): Parsed JSON content.  
    بيانات JSON بعد التحليل.
- **Attributes | الخصائص**:
  - `structure_type`: `"array" | "object" | "primitive"`
  - `total_items`: `int` (item count)
  - `complexity_score`: `float` (recursive complexity metric)
- **Methods | الدوال**:
  - `create_chunks(num_chunks: int = 40) -> List[Dict]`: Splits data into metadata-enriched chunks.  
    تقسيم البيانات إلى أجزاء مع بيانات وصفية.

### `PDFGenerator(output_dir: str = "output_pdfs")`

- **Parameters | المعاملات**:
  - `output_dir`: Directory path for PDFs.  
    مسار مجلد ملفات PDF.
- **Methods | الدوال**:
  - `generate_pdf(chunk_data: Dict, filename: str) -> bool`: Renders and saves a single PDF.  
    توليد وحفظ ملف PDF واحد.

### `JSONToPDFConverter(input_file: str, output_dir: str, num_files: int)`

- **Parameters | المعاملات**: as above in configuration.  
  كما في خيارات الإعداد أعلاه.
- **Methods | الدوال**:
  - `convert() -> bool`: Executes the end-to-end workflow, returns `True` on success.  
    تنفيذ عملية التحويل بالكامل، وتعيد True عند النجاح.

---

## 🔗 Dependencies & Compatibility  
## 🔗 التوافق والمتطلبات

- **Dependencies | المتطلبات**:
  - `reportlab>=3.6`
  - `tqdm>=4.60`
- **Python Versions | إصدارات بايثون**: Supported on Python 3.7+  
  مدعوم على بايثون 3.7 فأعلى
- **Tested On | تم الاختبار على**: Linux, macOS, Windows 10+

---

## 🤝 Contributing  
## 🤝 المساهمة

We welcome contributions! Please follow these steps:  
نرحب بمساهماتكم! يرجى اتباع الخطوات التالية:

1. Fork the repository.  
   قم بعمل Fork للمستودع.
2. Create a feature branch: `git checkout -b feature/YourFeature`.  
   أنشئ فرعًا جديدًا للميزة.
3. Commit your changes: `git commit -m "Add your message here"`.  
   أضف التعديلات والتعليق المناسب.
4. Push to the branch: `git push origin feature/YourFeature`.  
   ادفع التغييرات إلى الفرع الجديد.
5. Open a Pull Request and describe your changes.  
   افتح طلب دمج واشرح التعديلات.

**Coding Standards | معايير البرمجة**:

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.  
  اتبع دليل تنسيق كود بايثون PEP 8.
- Write meaningful commit messages.  
  اكتب رسائل توضيحية عند الالتزام.
- Include tests for new features or bug fixes.  
  أضف اختبارات للميزات الجديدة أو إصلاحات الأخطاء.

---

## ❓ FAQs & Troubleshooting  
## ❓ الأسئلة الشائعة وحلول المشاكل

**Q**: *I see `ImportError: ReportLab is required`*  
**س**: تظهر رسالة خطأ `ImportError: ReportLab is required`

**A**: Install ReportLab via `pip install reportlab`.  
**ج**: قم بتثبيت مكتبة ReportLab باستخدام الأمر `pip install reportlab`.

**Q**: *My JSON fails to parse*  
**س**: ملف JSON لا يتم تحليله بنجاح

**A**: Ensure valid JSON; the tool attempts repairs (quotes, booleans, nulls). For complex issues, validate with `jq` or online validators.  
**ج**: تأكد من صحة ملف JSON. الأداة تحاول الإصلاح تلقائيًا، لكن يفضل التحقق باستخدام أدوات خارجية مثل jq أو مواقع التحقق.

**Q**: *PDF generation is slow or fails on large datasets*  
**س**: توليد ملفات PDF بطيء أو يفشل مع البيانات الكبيرة

**A**: Use `--sequential` mode and increase `--timeout`. Reduce `--files` to split into larger chunks.  
**ج**: استخدم الوضع التسلسلي وزد المهلة الزمنية، أو قلل عدد الملفات الناتجة.

---