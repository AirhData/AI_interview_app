import React from 'react';
import '../style/Carte.css';
const Carte = ({children, ClassName}) => {
    const cardClassName = `carte ${className} || ''}`;
    return (
        <div className={cardClassName}>
            {children}
        </div>
    );
};

export default Carte;