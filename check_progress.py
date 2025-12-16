#!/usr/bin/env python3
"""
سكريبت فحص تقدم الترجمة
"""

import json
import os

INPUT_FILE = "translations_final.json"

def check_progress():
    """فحص تقدم الترجمة"""
    
    if not os.path.exists(INPUT_FILE):
        print("❌ الملف غير موجود: translations_final.json")
        print("   شغّل translate_texts.py أولاً")
        return
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = 0
    completed = 0
    needs_translation = 0
    
    for category in data.values():
        for item in category.values():
            total += 1
            
            if not item.get('needs_translation', True):
                completed += 1
            else:
                needs_translation += 1
    
    percentage = (completed / total * 100) if total > 0 else 0
    
    print("\n" + "="*50)
    print("📊 تقدم الترجمة:")
    print("="*50)
    print(f"إجمالي النصوص: {total}")
    print(f"✅ مترجم: {completed}")
    print(f"⏳ يحتاج ترجمة: {needs_translation}")
    print(f"\n📈 النسبة: {percentage:.1f}%")
    print("="*50)
    
    if needs_translation == 0:
        print("\n🎉 تهانينا! اكتملت جميع الترجمات!")
        print("\n📝 الخطوة التالية:")
        print("   python split_translations.py")
    else:
        remaining_runs = (needs_translation // 50) + 1
        print(f"\n⏳ متبقي حوالي {remaining_runs} تشغيل")
        print("\n📝 شغّل:")
        print("   python translate_texts.py")

if __name__ == "__main__":
    check_progress()
