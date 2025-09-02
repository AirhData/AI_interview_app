import '../style/Landing.css'; 
import Navbar from '../components/landing/Navbar';
import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import Footer from '../components/landing/Footer';


function Landing() {
  return (
    <div className="landing-container"> 
      <Navbar />
      <Hero />
      <Features />
      <Footer />
    </div>
  );
}

export default Landing;