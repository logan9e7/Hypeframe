from .database import Base, engine, SessionLocal
from .models import Moment

SEED = [
 ('gear-five','One Piece','The Drums of Liberation','Episode 1071','Transformation','An awakening changes the rhythm of battle.','#e3b45e'),
 ('sage-mode','Naruto Shippuden','The Hero Returns','Episode 163','Entrance','A hero arrives when the village needs him most.','#ee8d46'),
 ('super-saiyan','Dragon Ball Z','The First Super Saiyan','Episode 95','Transformation','A turning point that defined generations.','#f4c94c'),
 ('levi','Attack on Titan','Humanity’s Strongest','Season 3, Episode 17','Fight','Speed and precision in an unforgettable showdown.','#87a5b5'),
 ('gojo','Jujutsu Kaisen','Throughout Heaven and Earth','Season 2, Episode 4','Power','A moment of absolute confidence.','#b18cfc'),
 ('rengoku','Demon Slayer','Set Your Heart Ablaze','Mugen Train Arc','Emotional','A testament to conviction and courage.','#ee6a50'),
 ('eren','Attack on Titan','Declaration of War','Season 4, Episode 5','Twist','A declaration with world-changing consequences.','#b65f5f'),
 ('tanjiro','Demon Slayer','Hinokami Kagura','Episode 19','Fight','A breathtaking convergence of determination and artistry.','#fa715d'),
 ('luffy','One Piece','Nothing Happened','Episode 377','Emotional','Loyalty speaks loudest in silence.','#d2a26c'),
 ('mob','Mob Psycho 100','One Hundred Percent','Season 2','Power','Emotion meets extraordinary psychic force.','#78a9ef'),
 ('edward','Fullmetal Alchemist: Brotherhood','The Final Exchange','Episode 63','Emotional','The price of everything comes into focus.','#e1b974'),
 ('haikyuu','Haikyu!!','The Ultimate Rally','Season 3','Sports','Every second counts.','#e88a52'),
]

def seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for id, anime, title, episode, category, description, accent in SEED:
            if db.get(Moment, id) is None:
                db.add(Moment(id=id, anime=anime, title=title, episode=episode, category=category, description=description, accent=accent, spoiler=id!='haikyuu'))
        db.commit()

if __name__ == '__main__':
    seed()
