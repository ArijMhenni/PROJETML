import React from 'react'

function currency(num){
  try {
    return Number(num).toLocaleString(undefined, {maximumFractionDigits:0})
  } catch { return num }
}

export default function Results({data}){
  if(!data) return null
  return (
    <div style={{marginTop:12}}>
      <div className="result-card">
        <div style={{flex:1}}>
          <div className="price">{currency(data.prix_predit)} DT</div>
          <div className="sub">Estimation</div>
          <div style={{marginTop:8}}><strong>Marque:</strong> {data.marque} {data.modele}</div>
          <div className="sub">Année: {data.annee} • Kilométrage: {Number(data.kilometrage).toLocaleString()} km</div>
        </div>

        <div style={{textAlign:'right'}}>
          <div className="sub">Confiance</div>
          <div style={{marginTop:8}}><strong>{currency(data.prix_min)} DT</strong> — <strong>{currency(data.prix_max)} DT</strong></div>
          <div className="muted" style={{marginTop:10}}>Age: {data.age} ans</div>
        </div>
      </div>
    </div>
  )
}