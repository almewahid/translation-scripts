#!/usr/bin/env python3
"""
سكريبت ترجمة النصوص المستخرجة باستخدام Claude API
"""

import json
import os
import time
from anthropic import Anthropic

# ============================================
# الإعدادات
# ============================================

INPUT_FILE = "translations_extracted.json"
OUTPUT_FILE = "translations_final.json"

# Claude API
# ضع API Key الخاص بك هنا أو في متغير بيئة
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

if not API_KEY:
    print("❌ خطأ: يجب تعيين ANTHROPIC_API_KEY")
    print("   قم بتشغيل: export ANTHROPIC_API_KEY='your-key-here'")
    exit(1)

client = Anthropic(api_key=API_KEY)

# ============================================
# دوال الترجمة
# ============================================

def is_quranic_verse(text):
    """فحص إذا كان النص آية قرآنية"""
    # كلمات قرآنية مميزة
    quranic_indicators = [
        'قُلْ', 'إِنَّ', 'وَ', 'الَّذِينَ', 'يَا عِبَادِيَ',
        'لَا تَقْنَطُوا', 'رَّحْمَةِ', 'اللَّهِ', 'يُحِبُّ',
        'التَّوَّابِينَ', 'الْمُتَطَهِّرِينَ'
    ]
    
    # فحص التشكيل الكثيف (الآيات تحتوي تشكيل كامل)
    tashkeel_count = sum(1 for char in text if char in 'ًٌٍَُِّْ')
    text_length = len(text)
    
    # إذا كان أكثر من 30% من النص تشكيل → غالباً آية
    if text_length > 0 and (tashkeel_count / text_length) > 0.3:
        return True
    
    # إذا كان يحتوي كلمات قرآنية مميزة
    for indicator in quranic_indicators:
        if indicator in text:
            return True
    
    return False

def translate_text(text, source_lang, target_lang):
    """ترجمة نص واحد باستخدام Claude"""
    
    # تحديد اللغة المصدر
    lang_names = {
        'ar': 'Arabic',
        'en': 'English',
        'fr': 'French',
        'zh': 'Simplified Chinese'
    }
    
    prompt = f"""Translate the following {lang_names.get(source_lang, 'text')} to {lang_names[target_lang]}.

Important guidelines:
- Maintain Islamic terminology accurately
- Keep the tone formal and respectful
- For religious terms, use standard translations
- Return ONLY the translation, no explanations

Text to translate:
{text}

Translation:"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        translation = message.content[0].text.strip()
        return translation
    
    except Exception as e:
        print(f"❌ خطأ في الترجمة: {e}")
        return ""

def translate_batch(data, max_translations=50):
    """ترجمة مجموعة من النصوص"""
    
    translated_count = 0
    total_count = sum(
        len(category) for category in data.values()
    )
    
    print(f"\n🌐 بدء الترجمة ({total_count} نص)...\n")
    
    for category_name, category_data in data.items():
        print(f"📂 الفئة: {category_name}")
        
        for key, item in category_data.items():
            # تخطي إذا تمت الترجمة
            if not item.get('needs_translation', True):
                continue
            
            # تحديد اللغة المصدر
            source_text = item['ar'] if item['ar'] else item['en']
            source_lang = 'ar' if item['ar'] else 'en'
            
            if not source_text:
                continue
            
            # تخطي الآيات القرآنية
            if source_lang == 'ar' and is_quranic_verse(source_text):
                print(f"   ⏭️  تخطي آية قرآنية: {source_text[:30]}...")
                item['needs_translation'] = False
                continue
            
            print(f"   • {key[:30]}...")
            
            # ترجمة للغات المطلوبة
            if source_lang == 'ar':
                # ترجمة من العربية
                if not item['en']:
                    item['en'] = translate_text(source_text, 'ar', 'en')
                    time.sleep(1)  # سرعة متوسطة
                
                if not item['fr']:
                    item['fr'] = translate_text(source_text, 'ar', 'fr')
                    time.sleep(1)
                
                if not item['zh']:
                    item['zh'] = translate_text(source_text, 'ar', 'zh')
                    time.sleep(1)
            
            else:
                # ترجمة من الإنجليزية
                if not item['ar']:
                    item['ar'] = translate_text(source_text, 'en', 'ar')
                    time.sleep(1)
                
                if not item['fr']:
                    item['fr'] = translate_text(source_text, 'en', 'fr')
                    time.sleep(1)
                
                if not item['zh']:
                    item['zh'] = translate_text(source_text, 'en', 'zh')
                    time.sleep(1)
            
            item['needs_translation'] = False
            translated_count += 1
            
            # حد أقصى للترجمات في كل تشغيل
            if max_translations and translated_count >= max_translations:
                print(f"\n⚠️  تم الوصول للحد الأقصى ({max_translations} نص)")
                print(f"   شغّل السكريبت مرة أخرى لإكمال الترجمة")
                return data
        
        print()
    
    print(f"✅ تمت ترجمة {translated_count} نص")
    return data

# ============================================
# توليد ملف translations.jsx
# ============================================

def generate_translations_jsx(data):
    """توليد ملف translations.jsx من البيانات"""
    
    output = "export const translations = {\n"
    
    languages = ['ar', 'en', 'fr', 'zh']
    lang_comments = {
        'ar': 'Arabic',
        'en': 'English',
        'fr': 'Français',
        'zh': 'Chinese (Simplified)'
    }
    
    for lang in languages:
        output += f"  // ============================================\n"
        output += f"  // {lang_comments[lang]}\n"
        output += f"  // ============================================\n"
        output += f"  {lang}: {{\n"
        
        for category_name, category_data in sorted(data.items()):
            output += f"    // ============ {category_name} ============\n"
            output += f"    {category_name}: {{\n"
            
            for key, item in sorted(category_data.items()):
                value = item.get(lang, '').replace('\\', '\\\\').replace('"', '\\"')
                output += f'      {key}: "{value}",\n'
            
            output += f"    }},\n\n"
        
        output += f"  }},\n\n"
    
    output += "};\n"
    
    return output

# ============================================
# التشغيل
# ============================================

if __name__ == "__main__":
    print("🚀 بدء ترجمة النصوص...\n")
    
    # قراءة البيانات
    if not os.path.exists(INPUT_FILE):
        print(f"❌ الملف غير موجود: {INPUT_FILE}")
        print(f"   قم بتشغيل extract_texts.py أولاً")
        exit(1)
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # ترجمة النصوص
    # غيّر max_translations=None لترجمة كل شيء
    translated_data = translate_batch(data, max_translations=200)
    
    # حفظ النتائج
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم حفظ النتائج في: {OUTPUT_FILE}")
    
    # توليد ملف translations.jsx
    jsx_content = generate_translations_jsx(translated_data)
    
    with open("translations_GENERATED.jsx", 'w', encoding='utf-8') as f:
        f.write(jsx_content)
    
    print(f"✅ تم توليد: translations_GENERATED.jsx")
    
    # صوت تنبيه عند الانتهاء
    print('\a')  # Bell sound
    print('\a')
    print('\a')
    
    print(f"\n📝 الخطوة التالية:")
    print(f"   1. راجع ملف translations_GENERATED.jsx")
    print(f"   2. انسخه إلى src/components/translations.jsx")
    print(f"   3. شغّل السكريبت مرة أخرى إذا بقيت ترجمات")