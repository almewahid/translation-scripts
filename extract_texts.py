#!/usr/bin/env python3
"""
سكريبت ترجمة صفحات الموقع تلقائياً
يستخرج النصوص العربية والإنجليزية من ملفات JSX ويترجمها لـ 4 لغات
"""

import re
import json
import os
from pathlib import Path

# ============================================
# الإعدادات
# ============================================

# المجلدات
PAGES_DIR = "src/pages"
OUTPUT_FILE = "translations_extracted.json"

# أنماط البحث عن النصوص
PATTERNS = {
    # نصوص بين علامات تنصيص مزدوجة
    'double_quotes': r'"([^"]{3,})"',
    # نصوص بين علامات تنصيص مفردة  
    'single_quotes': r"'([^']{3,})'",
    # نصوص في JSX
    'jsx_text': r'>\s*([^<>{}\n]{3,})\s*<',
}

# أنماط لتجاهلها
IGNORE_PATTERNS = [
    r'^[a-zA-Z0-9_\-\.\/]+$',  # أسماء ملفات ومتغيرات
    r'^className$',
    r'^onClick$',
    r'^onChange$',
    r'^\d+$',  # أرقام فقط
    r'^[a-z]+\.[a-z]+$',  # مثل item.title
    r'^t\(',  # استدعاءات t() موجودة
    r'^\$',  # متغيرات
    r'^https?://',  # روابط
]

# ============================================
# دوال مساعدة
# ============================================

def is_arabic(text):
    """فحص إذا كان النص يحتوي على عربي"""
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))

def is_chinese(text):
    """فحص إذا كان النص يحتوي على صيني"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(text))

def should_ignore(text):
    """فحص إذا كان النص يجب تجاهله"""
    text = text.strip()
    
    # نصوص قصيرة جداً
    if len(text) < 3:
        return True
    
    # تحقق من الأنماط المتجاهلة
    for pattern in IGNORE_PATTERNS:
        if re.match(pattern, text):
            return True
    
    return False

def clean_text(text):
    """تنظيف النص"""
    # إزالة المسافات الزائدة
    text = ' '.join(text.split())
    # إزالة الأحرف الخاصة في البداية والنهاية
    text = text.strip('.,;:!?()[]{}\'\"')
    return text

def extract_texts_from_file(file_path):
    """استخراج جميع النصوص من ملف JSX"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ خطأ في قراءة {file_path}: {e}")
        return []
    
    texts = set()
    
    # استخراج النصوص باستخدام الأنماط المختلفة
    for pattern_name, pattern in PATTERNS.items():
        matches = re.findall(pattern, content)
        for match in matches:
            text = clean_text(match)
            
            # تجاهل النصوص غير المناسبة
            if should_ignore(text):
                continue
            
            # إضافة النصوص العربية والإنجليزية فقط
            if is_arabic(text) or (len(text) > 5 and text[0].isupper()):
                texts.add(text)
    
    return list(texts)

def generate_translation_key(text, existing_keys):
    """توليد مفتاح ترجمة فريد"""
    # إزالة الأحرف الخاصة
    key = re.sub(r'[^\w\s]', '', text.lower())
    # استبدال المسافات بـ _
    key = '_'.join(key.split())
    # تقصير إلى 50 حرف
    key = key[:50]
    
    # التأكد من عدم التكرار
    original_key = key
    counter = 1
    while key in existing_keys:
        key = f"{original_key}_{counter}"
        counter += 1
    
    return key

def categorize_text(text, file_name):
    """تحديد الفئة المناسبة للنص"""
    file_lower = file_name.lower()
    
    # حسب اسم الملف
    if 'home' in file_lower:
        return 'home'
    elif 'repentance' in file_lower or 'tawba' in file_lower:
        return 'repentance'
    elif 'fatwa' in file_lower:
        return 'fatwa'
    elif 'learn' in file_lower or 'islam' in file_lower:
        return 'learn_islam'
    elif 'contact' in file_lower:
        return 'contact'
    elif 'course' in file_lower:
        return 'courses'
    elif 'profile' in file_lower:
        return 'profile'
    elif 'reconciliation' in file_lower:
        return 'reconciliation'
    
    # حسب محتوى النص
    text_lower = text.lower()
    if any(word in text_lower for word in ['login', 'register', 'password', 'email']):
        return 'auth'
    elif any(word in text_lower for word in ['search', 'filter', 'find']):
        return 'search'
    elif any(word in text_lower for word in ['save', 'delete', 'edit', 'cancel']):
        return 'common'
    
    return 'common'

# ============================================
# الوظيفة الرئيسية
# ============================================

def extract_all_texts(pages_directory):
    """استخراج جميع النصوص من كل الملفات"""
    
    if not os.path.exists(pages_directory):
        print(f"❌ المجلد غير موجود: {pages_directory}")
        return {}
    
    all_texts = {}
    existing_keys = set()
    
    # قراءة جميع ملفات JSX
    jsx_files = list(Path(pages_directory).rglob('*.jsx'))
    
    print(f"\n🔍 جاري فحص {len(jsx_files)} ملف...\n")
    
    for file_path in jsx_files:
        file_name = file_path.stem
        print(f"📄 {file_name}.jsx")
        
        # استخراج النصوص
        texts = extract_texts_from_file(file_path)
        
        if not texts:
            print(f"   ⚠️  لم يتم العثور على نصوص\n")
            continue
        
        print(f"   ✅ تم استخراج {len(texts)} نص\n")
        
        # معالجة كل نص
        for text in texts:
            # تحديد الفئة
            category = categorize_text(text, file_name)
            
            # توليد مفتاح
            key = generate_translation_key(text, existing_keys)
            existing_keys.add(key)
            
            # إضافة للنتائج
            if category not in all_texts:
                all_texts[category] = {}
            
            all_texts[category][key] = {
                'ar': text if is_arabic(text) else '',
                'en': text if not is_arabic(text) else '',
                'fr': '',
                'zh': '',
                'source_file': file_name,
                'needs_translation': True
            }
    
    return all_texts

def save_results(data, output_file):
    """حفظ النتائج في ملف JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم حفظ النتائج في: {output_file}")

def print_statistics(data):
    """طباعة إحصائيات"""
    total_texts = sum(len(category) for category in data.values())
    arabic_texts = sum(
        1 for category in data.values() 
        for item in category.values() 
        if item['ar']
    )
    english_texts = sum(
        1 for category in data.values() 
        for item in category.values() 
        if item['en']
    )
    
    print("\n" + "="*50)
    print("📊 الإحصائيات:")
    print("="*50)
    print(f"إجمالي النصوص: {total_texts}")
    print(f"نصوص عربية: {arabic_texts}")
    print(f"نصوص إنجليزية: {english_texts}")
    print(f"\nالفئات:")
    for category, items in data.items():
        print(f"  • {category}: {len(items)} نص")
    print("="*50)

# ============================================
# التشغيل
# ============================================

if __name__ == "__main__":
    print("🚀 بدء استخراج النصوص من ملفات JSX...\n")
    
    # استخراج النصوص
    extracted_data = extract_all_texts(PAGES_DIR)
    
    if not extracted_data:
        print("\n❌ لم يتم العثور على أي نصوص!")
    else:
        # حفظ النتائج
        save_results(extracted_data, OUTPUT_FILE)
        
        # طباعة الإحصائيات
        print_statistics(extracted_data)
        
        print(f"\n✨ تم الانتهاء!")
        print(f"\n📝 الخطوة التالية:")
        print(f"   1. راجع ملف {OUTPUT_FILE}")
        print(f"   2. شغّل سكريبت الترجمة: python translate_texts.py")
