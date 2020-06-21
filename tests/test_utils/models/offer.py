from enum import Enum
from datetime import datetime
from typing import Iterable
from sqlalchemy import BigInteger, Column, DateTime, desc, ForeignKey, String
from sqlalchemy import and_, ARRAY, Boolean, CheckConstraint, false, Integer, Text, TEXT
from sqlalchemy.orm import column_property
from sqlalchemy.sql import select, func
from sqlalchemy_api_handler import ApiHandler
from sqlalchemy_api_handler.serialization.as_dict import as_dict
from sqlalchemy_api_handler.utils.date import DateTimes

from tests.test_utils.db import Model
from tests.test_utils.models.stock import Stock


class SearchableType(Enum):
    @classmethod
    def find_from_sub_labels(cls, sub_labels):
        matching_types = []
        comparable_sub_labels = [label.lower() for label in sub_labels]

        for type in cls:
            if type.value['sublabel'].lower() in comparable_sub_labels:
                matching_types.append(type)

        return matching_types

class ThingType(SearchableType):
    ACTIVATION = {
        'proLabel': 'Pass Culture : activation en ligne',
        'appLabel': 'Pass Culture : activation en ligne',
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': 'Activation',
        'description': 'Activez votre pass Culture grâce à cette offre',
        'conditionalFields': [],
        'isActive': True
    }
    AUDIOVISUEL = {
        'proLabel': "Audiovisuel — films sur supports physiques et VOD",
        'appLabel': "Films sur supports physiques et VOD",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': [],
        'isActive': True
    }
    CINEMA_ABO = {
        'proLabel': "Cinéma — abonnements",
        'appLabel': "Abonnements",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': [],
        'isActive': True
    }
    JEUX = {
        'proLabel': "Jeux (support physique)",
        'appLabel': "Support physique",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': [],
        'isActive': False
    }
    JEUX_VIDEO_ABO = {
        'proLabel': "Jeux — abonnements",
        'appLabel': "Jeux — abonnements",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': [],
        'isActive': True
    }
    JEUX_VIDEO = {
        'proLabel': "Jeux vidéo",
        'appLabel': "Jeux vidéo",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Jouer",
        'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
        'conditionalFields': [],
        'isActive': True
    }
    LIVRE_AUDIO = {
        'proLabel': "Livre audio numérique",
        'appLabel': "Livre audio numérique",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Lire",
        'description': "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
        'conditionalFields': ["author"],
        'isActive': True
    }
    LIVRE_EDITION = {
        'proLabel': "Livre - format papier ou numérique, abonnements lecture",
        'appLabel': "Livres, cartes bibliothèque ou médiathèque",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Lire",
        'description': "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
        'conditionalFields': ["author", "isbn"],
        'isActive': True
    }
    MUSEES_PATRIMOINE_ABO = {
        'proLabel': "Musées, arts visuels & patrimoine",
        'appLabel': "Visites libres et abonnements",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': [],
        'isActive': True
    }
    MUSIQUE_ABO = {
        'proLabel': "Musique — abonnements concerts",
        'appLabel': "Abonnements concerts",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?",
        'conditionalFields': ["musicType"],
        'isActive': True
    }
    MUSIQUE = {
        'proLabel': "Musique (sur supports physiques ou en ligne)",
        'appLabel': "Supports physiques ou en ligne",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Écouter",
        'description': "Plutôt rock, rap ou classique ? Sur un smartphone avec des écouteurs ou entre amis au concert ?",
        'conditionalFields': ["author", "musicType", "performer"],
        'isActive': True
    }
    OEUVRE_ART = {
        'proLabel': "Vente d'œuvres d'art",
        'appLabel': "Achat d'œuvres d’art",
        'offlineOnly': False,
        'onlineOnly': False,
        'sublabel': "Regarder",
        'description': "Action, science-fiction, documentaire ou comédie sentimentale ? En salle, en plein air ou bien au chaud chez soi ? Et si c’était plutôt cette exposition qui allait faire son cinéma ?",
        'conditionalFields': [],
        'isActive': True
    }
    PRATIQUE_ARTISTIQUE_ABO = {
        'proLabel': "Pratique artistique — abonnements",
        'appLabel': "Pratique artistique — abonnements",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer",
        'description': "Jamais osé monter sur les planches ? Tenter d’apprendre la guitare, le piano ou la photographie ? Partir cinq jours découvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?",
        'conditionalFields': ['speaker'],
        'isActive': True
    }
    PRESSE_ABO = {
        'proLabel': "Presse — abonnements",
        'appLabel': "Presse — abonnements",
        'offlineOnly': False,
        'onlineOnly': True,
        'sublabel': "Lire",
        'description': "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
        'conditionalFields': [],
        'isActive': True
    }
    INSTRUMENT = {
        'proLabel': "Vente et location d’instruments de musique",
        'appLabel': "Achat et location d’instruments de musique",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Pratiquer",
        'description': "Jamais osé monter sur les planches ? Tenter d’apprendre la guitare, le piano ou la photographie ? Partir cinq jours découvrir un autre monde ? Bricoler dans un fablab, ou pourquoi pas, enregistrer votre premier titre ?",
        'conditionalFields': [],
        'isActive': True
    }
    SPECTACLE_VIVANT_ABO = {
        'proLabel': "Spectacle vivant — abonnements",
        'appLabel': "Spectacle vivant — abonnements",
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': "Applaudir",
        'description': "Suivre un géant de 12 mètres dans la ville ? Rire aux éclats devant un stand up ? Rêver le temps d’un opéra ou d’un spectacle de danse ? Assister à une pièce de théâtre, ou se laisser conter une histoire ?",
        'conditionalFields': ["showType"],
        'isActive': True
    }

@as_dict.register(ThingType)
def _(thing_type, column=None, includes: Iterable = ()):
    dict_value = {
        'type': 'Thing',
        'value': str(thing_type),
    }
    dict_value.update(thing_type.value)
    return dict_value


class ProductType:
    @classmethod
    def is_thing(cls, name: str) -> object:
        for possible_type in list(ThingType):
            if str(possible_type) == name:
                return True

        return False


class Offer(ApiHandler,
            Model):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    bookingEmail = Column(String(120), nullable=True)

    type = Column(String(50),
                  CheckConstraint("type != 'None'"),
                  index=True,
                  nullable=False)

    name = Column(String(140), nullable=False)

    description = Column(Text, nullable=True)

    conditions = Column(String(120),
                        nullable=True)

    ageMin = Column(Integer,
                    nullable=True)
    ageMax = Column(Integer,
                    nullable=True)

    url = Column(String(255), nullable=True)

    mediaUrls = Column(ARRAY(String(220)),
                       nullable=False,
                       default=[])

    durationMinutes = Column(Integer, nullable=True)

    isNational = Column(Boolean,
                        server_default=false(),
                        default=False,
                        nullable=False)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    @property
    def dateRange(self):
        if ProductType.is_thing(self.type) or not self.notDeletedStocks:
            return DateTimes()

        start = min([stock.beginningDatetime for stock in self.notDeletedStocks])
        end = max([stock.endDatetime for stock in self.notDeletedStocks])
        return DateTimes(start, end)

    @property
    def notDeletedStocks(self):
        return [stock for stock in self.stocks if not stock.isSoftDeleted]
