"""
Protection contre les attaques par force brute sur la connexion.

Principe : après trop d'échecs sur une même clé pendant la fenêtre observée, la clé est bloquée
un certain temps (réponse HTTP 429). Deux clés sont surveillées pour chaque tentative :
  - "adresse IP | email" : 5 échecs en 15 minutes => blocage de 15 minutes ;
  - "adresse IP" seule   : 20 échecs en 15 minutes => blocage de 15 minutes (essais sur plusieurs comptes).
La clé inclut l'adresse IP : un attaquant ne peut donc pas bloquer le compte d'un autre utilisateur
depuis sa propre machine.

Limite assumée : les compteurs sont en mémoire du processus (ils sont remis à zéro au redémarrage
du serveur et ne sont pas partagés entre plusieurs processus). C'est suffisant pour ce projet.
"""
import threading
import time
from collections import deque

FENETRE_SECONDES = 15 * 60
DUREE_BLOCAGE_SECONDES = 15 * 60
MAX_ECHECS_PAR_COUPLE = 5
MAX_ECHECS_PAR_IP = 20
_TAILLE_MAX_MEMOIRE = 10_000


class LoginGuard:
    def __init__(self) -> None:
        self._verrou = threading.Lock()
        self._echecs: dict[str, deque[float]] = {}
        self._bloque_jusqua: dict[str, float] = {}

    @staticmethod
    def cles(ip: str, email: str) -> list[tuple[str, int]]:
        """Clés surveillées pour une tentative, avec le nombre d'échecs maximal de chacune."""
        return [(f"couple:{ip}|{email.lower().strip()}", MAX_ECHECS_PAR_COUPLE), (f"ip:{ip}", MAX_ECHECS_PAR_IP)]

    def secondes_restantes(self, ip: str, email: str) -> int:
        """Nombre de secondes avant la fin du blocage (0 si la connexion est autorisée)."""
        maintenant = time.monotonic()
        with self._verrou:
            restant = 0.0
            for cle, _ in self.cles(ip, email):
                fin = self._bloque_jusqua.get(cle)
                if fin is None:
                    continue
                if fin <= maintenant:
                    del self._bloque_jusqua[cle]
                    self._echecs.pop(cle, None)
                else:
                    restant = max(restant, fin - maintenant)
            return int(restant) + 1 if restant > 0 else 0

    def enregistrer_echec(self, ip: str, email: str) -> None:
        maintenant = time.monotonic()
        with self._verrou:
            if len(self._echecs) > _TAILLE_MAX_MEMOIRE:
                self._nettoyer(maintenant)
            for cle, maximum in self.cles(ip, email):
                echecs = self._echecs.setdefault(cle, deque())
                echecs.append(maintenant)
                while echecs and echecs[0] < maintenant - FENETRE_SECONDES:
                    echecs.popleft()
                if len(echecs) >= maximum:
                    self._bloque_jusqua[cle] = maintenant + DUREE_BLOCAGE_SECONDES

    def reinitialiser_couple(self, ip: str, email: str) -> None:
        """Après une connexion réussie : on efface les échecs de ce couple (pas ceux de l'IP)."""
        cle = self.cles(ip, email)[0][0]
        with self._verrou:
            self._echecs.pop(cle, None)
            self._bloque_jusqua.pop(cle, None)

    def reinitialiser_tout(self) -> None:
        with self._verrou:
            self._echecs.clear()
            self._bloque_jusqua.clear()

    def _nettoyer(self, maintenant: float) -> None:
        for cle in [c for c, e in self._echecs.items() if not e or e[-1] < maintenant - FENETRE_SECONDES]:
            self._echecs.pop(cle, None)
            self._bloque_jusqua.pop(cle, None)


login_guard = LoginGuard()
