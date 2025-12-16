#!/usr/bin/env python3
"""
سكريبت تقسيم translations.jsx إلى ملفات منفصلة لكل لغة
"""

import re
import os

INPUT_FILE = "translations_GENERATED.jsx"
OUTPUT_DIR = "src/locales"

def ensure_dir(directory):
    """إنشاء المجلد إذا لم يكن موجوداً"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"✅ تم إنشاء المجلد: {directory}")

def split_translations():
    """تقسيم الترجمات إلى ملفات منفصلة"""
    
    print("🚀 بدء تقسيم ملف الترجمات...\n")
    
    # قراءة الملف
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف غير موجود: {INPUT_FILE}")
        return
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استخراج كل لغة
    languages = {
        'ar': 'العربية',
        'en': 'English',
        'fr': 'Français',
        'zh': '中文'
    }
    
    # إنشاء المجلدات
    ensure_dir(OUTPUT_DIR)
    
    for lang_code, lang_name in languages.items():
        print(f"📝 معالجة {lang_name} ({lang_code})...")
        
        # البحث عن قسم اللغة
        pattern = rf'{lang_code}:\s*\{{(.*?)\n  \}},'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print(f"   ⚠️  لم يتم العثور على {lang_name}")
            continue
        
        lang_content = match.group(1)
        
        # إنشاء ملف اللغة
        output_file = f"{OUTPUT_DIR}/{lang_code}.js"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"// {lang_name} translations\n")
            f.write(f"export const {lang_code} = {{\n")
            f.write(lang_content)
            f.write("\n};\n")
        
        # حساب عدد الأسطر
        lines = lang_content.count('\n')
        print(f"   ✅ تم حفظ {output_file} ({lines} سطر)\n")
    
    # إنشاء ملف index.js
    create_index_file()
    
    print("✨ تم الانتهاء من التقسيم!")

def create_index_file():
    """إنشاء ملف index.js لتجميع كل الترجمات"""
    
    index_content = """// Auto-generated translations index
import { ar } from './ar';
import { en } from './en';
import { fr } from './fr';
import { zh } from './zh';

export const translations = {
  ar,
  en,
  fr,
  zh,
};
"""
    
    index_file = f"{OUTPUT_DIR}/index.js"
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"✅ تم إنشاء {index_file}")

def update_language_context():
    """تحديث LanguageContext.jsx ليستخدم الملفات المنفصلة"""
    
    context_file = "src/components/LanguageContext.jsx"
    
    if not os.path.exists(context_file):
        print(f"\n⚠️  الملف غير موجود: {context_file}")
        print("   يجب تحديث LanguageContext.jsx يدوياً")
        return
    
    print(f"\n📝 تحديث {context_file}...")
    
    with open(context_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استبدال import
    old_import = "import { translations } from './translations';"
    new_import = "import { translations } from '../locales';"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ تم التحديث بنجاح!")
    else:
        print("   ⚠️  لم يتم العثور على السطر المطلوب")
        print("   غيّر السطر يدوياً من:")
        print(f"      {old_import}")
        print("   إلى:")
        print(f"      {new_import}")

if __name__ == "__main__":
    split_translations()
    update_language_context()
    
    print("\n" + "="*50)
    print("📊 النتيجة:")
    print("="*50)
    print("✅ تم تقسيم الترجمات إلى:")
    print("   • src/locales/ar.js")
    print("   • src/locales/en.js")
    print("   • src/locales/fr.js")
    print("   • src/locales/zh.js")
    print("   • src/locales/index.js")
    print("\n💡 الفوائد:")
    print("   • ملفات أصغر وأسهل في التعديل")
    print("   • تحميل أسرع (lazy loading)")
    print("   • تنظيم أفضل")
    print("="*50)
