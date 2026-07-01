import asyncio

from sqlalchemy import select

from app.models import Category, FileFormat, Scenario
from app.models.base import async_session

CATEGORIES = [
    "Mustaqillik bayrami",
    "Konstitutsiya kuni",
    "Navro'z",
    "So'nggi qo'ng'iroq",
    "Bilimlar kuni",
    "O'qituvchilar kuni",
    "Zakovat",
    "Besh tashabbus",
    "Ma'naviy-ma'rifiy tadbirlar",
    "Talabalar festivali",
    "Universitet tadbirlari",
    "Maktab tadbirlari",
    "Bolalar bog'chasi",
    "Tanlovlar",
    "Sport tadbirlari",
    "Boshqa",
]

SAMPLE = [
    ("Mustaqillik bayrami tantanasi", "1-sentyabr uchun to'liq ssenariy", 35000, 12, "Mustaqillik bayrami"),
    ("Navro'z bayrami dasturi", "Bahor bayrami uchun she'r va sahna ko'rinishlari", 30000, 10, "Navro'z"),
    ("So'nggi qo'ng'iroq 2025", "Bitiruvchilar uchun ta'sirli ssenariy", 28000, 8, "So'nggi qo'ng'iroq"),
    ("Bilimlar kuni ochilish", "Yangi o'quv yili tantanasi", 25000, 7, "Bilimlar kuni"),
    ("Zakovat intellektual o'yini", "Savol-javoblar to'plami bilan", 40000, 15, "Zakovat"),
]


async def seed() -> None:
    async with async_session() as session:
        existing = await session.scalar(select(Category).limit(1))
        if existing:
            print("Already seeded.")
            return

        cat_map: dict[str, Category] = {}
        for i, name in enumerate(CATEGORIES):
            c = Category(name_uz=name, sort_order=i)
            session.add(c)
            cat_map[name] = c
        await session.flush()

        for title, desc, price, pages, cat in SAMPLE:
            session.add(
                Scenario(
                    category_id=cat_map[cat].id,
                    title=title,
                    description=desc,
                    keywords=f"{title} {cat}".lower(),
                    price=price,
                    pages=pages,
                    file_format=FileFormat.docx,
                    rating=4.5,
                )
            )
        await session.commit()
        print(f"Seeded {len(CATEGORIES)} categories, {len(SAMPLE)} scenarios.")


if __name__ == "__main__":
    asyncio.run(seed())
