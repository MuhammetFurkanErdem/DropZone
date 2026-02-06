"""
Utility Functions
Yardımcı fonksiyonlar
"""

import random
import string


def generate_room_code(length: int = 6) -> str:
    """
    Okunabilir, benzersiz bir oda kodu üretir.
    Format: XXX-XXX (örn: A7X-29K)
    
    Args:
        length: Kod uzunluğu (varsayılan: 6)
    
    Returns:
        str: Üretilen oda kodu
    """
    # Karışık harfler ve sayılar (0, O, I, l gibi karıştırılabilecekleri hariç tut)
    chars = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '')
    
    # İlk yarı
    first_part = ''.join(random.choice(chars) for _ in range(length // 2))
    # İkinci yarı
    second_part = ''.join(random.choice(chars) for _ in range(length // 2))
    
    return f"{first_part}-{second_part}"


def generate_unique_room_code(db, max_attempts: int = 10) -> str:
    """
    Veritabanında benzersiz olan bir oda kodu üretir.
    
    Args:
        db: Database session
        max_attempts: Maksimum deneme sayısı
    
    Returns:
        str: Benzersiz oda kodu
    
    Raises:
        ValueError: Benzersiz kod üretilemezse
    """
    from models import Room
    
    for _ in range(max_attempts):
        code = generate_room_code()
        # Kodun veritabanında olup olmadığını kontrol et
        existing = db.query(Room).filter(Room.room_id == code).first()
        if not existing:
            return code
    
    raise ValueError("Benzersiz oda kodu üretilemedi. Lütfen tekrar deneyin.")
