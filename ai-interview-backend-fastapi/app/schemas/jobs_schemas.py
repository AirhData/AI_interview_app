from pydantic import BaseModel, Field
from typing import Optional

class JobOffer(BaseModel):
    """
    Schéma de données pour une offre d'emploi.
    Valide les données entrantes de l'API externe et sortantes de notre API.
    """
    id: str
    entreprise: Optional[str] = None
    ville: Optional[str] = None
    poste: Optional[str] = None
    contrat: Optional[str] = None
    description_poste: Optional[str] = Field(None, alias="description_poste")
    publication: Optional[str] = None
    lien: Optional[str] = None
    description_nettoyee: Optional[str] = Field(None, alias="description_nettoyee")
    mission: Optional[str] = None
    profil_recherche: Optional[str] = Field(None, alias="profil_recherche")
    competences: Optional[str] = None
    pole: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True