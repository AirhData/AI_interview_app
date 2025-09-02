import candidatImg from '../../assets/candidat.png';
import recruteurImg from '../../assets/recruteur.png';

function Features() {
  return (
    <section className="features-section">
      <div className="feature-card">
        <img src={candidatImg} alt="Candidat" className="feature-image" />
        <h2 className="feature-title">Pour les Candidats</h2>
        <ul className="feature-list">
          <li><strong>Entraînez-vous de manière ciblée :</strong> Nous travaillons à vous proposer des simulations basées sur les compétences clés recherchées dans les offres d'emploi et celles présentes dans votre CV.</li>
          <li><strong>Recevez des retours constructifs :</strong> Nous souhaitons vous fournir une analyse de vos réponses pour vous aider à identifier vos points forts et les aspects à améliorer.</li>
          <li><strong>Gagnez en assurance :</strong> Notre but est de vous permettre de vous familiariser avec le format des entretiens et de réduire le stress lié à cette étape cruciale.</li>
        </ul>
      </div>

      <div className="feature-card">
        <img src={recruteurImg} alt="Recruteur" className="feature-image" />
        <h2 className="feature-title">Pour les Recruteurs</h2>
        <ul className="feature-list">
          <li><strong>Optimisez votre processus de sélection :</strong> Nous cherchons à vous offrir un outil pour évaluer les candidats de manière plus efficace et structurée.</li>
          <li><strong>Gagnez du temps dans la présélection :</strong> Nous souhaitons vous aider à identifier rapidement les profils les plus prometteurs pour les postes à pourvoir.</li>
          <li><strong>Obtenez des informations pertinentes :</strong> Notre objectif est de vous fournir des rapports d'évaluation pour faciliter vos décisions d'embauche.</li>
        </ul>
      </div>
    </section>
  );
}

export default Features;