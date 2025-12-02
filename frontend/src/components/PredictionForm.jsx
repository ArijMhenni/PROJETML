import React, { useEffect, useState } from 'react'
import axios from 'axios'
import Results from './Results'

const defaultVehicle = {
  marque: '',
  modele: '',
  annee: new Date().getFullYear(),
  kilometrage: 50000,
  energie: 'Diesel',
  boite_vitesses: 'Manuelle',
  puissance_fiscale: 7
}

export default function PredictionForm(){
  const [brands, setBrands] = useState([])
  const [energies, setEnergies] = useState(['Diesel', 'Essence', 'Hybride', 'Electrique', 'GPL'])
  const [boites, setBoites] = useState(['Manuelle', 'Automatique'])
  const [vehicle, setVehicle] = useState({...defaultVehicle})
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    axios.get('/api/brands')
      .then(res => {
        if(!mounted) return
        if(res.data && res.data.success){
          setBrands(res.data.marques || [])
          setEnergies(res.data.energies || energies)
          setBoites(res.data.boites || boites)
          // preselect first brand if empty
          setVehicle(v => ({...v, marque: (res.data.marques && res.data.marques[0]) || v.marque}))
        } else {
          setError('Impossible de récupérer la liste des marques.')
        }
      })
      .catch(err => {
        console.error(err)
        setError('Erreur réseau lors de récupération des marques.')
      })
    return ()=> mounted = false
  }, [])

  function onChange(e){
    const {name, value} = e.target
    setVehicle(v => ({...v, [name]: name === 'kilometrage' || name === 'annee' || name === 'puissance_fiscale' ? Number(value) : value}))
  }

  async function onSubmit(e){
    e.preventDefault()
    setError(null)
    setResult(null)

    // Basic validation
    if(!vehicle.marque){
      setError('Veuillez sélectionner une marque.')
      return
    }
    if(vehicle.annee < 1900 || vehicle.annee > new Date().getFullYear()){
      setError('Année invalide.')
      return
    }
    if(vehicle.kilometrage < 0){
      setError('Kilométrage invalide.')
      return
    }

    try {
      setLoading(true)
      const res = await axios.post('/api/predict', vehicle)
      if(res.data && res.data.success){
        setResult(res.data)
      } else {
        setError(res.data.error || 'Erreur lors de la prédiction.')
      }
    } catch (err) {
      console.error(err)
      const msg = err.response?.data?.error || err.message || 'Erreur réseau'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Estimateur de prix</h2>
      <p className="muted">Renseignez les détails du véhicule et cliquez sur <strong>Prédire</strong>.</p>

      <form className="form" onSubmit={onSubmit}>

        <div className="row">
          <div className="field">
            <label>Marque</label>
            <select name="marque" value={vehicle.marque} onChange={onChange} className="input" required>
              <option value="">-- Sélectionner --</option>
              {brands.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>

          <div className="field">
            <label>Modèle</label>
            <input className="input" name="modele" value={vehicle.modele} onChange={onChange} placeholder="e.g., Série 3"/>
          </div>
        </div>

        <div className="row">
          <div className="field">
            <label>Année</label>
            <input className="input" type="number" name="annee" value={vehicle.annee} onChange={onChange} min="1900" max={new Date().getFullYear()} />
          </div>

          <div className="field">
            <label>Kilométrage</label>
            <input className="input" type="number" name="kilometrage" value={vehicle.kilometrage} onChange={onChange} min="0" />
          </div>
        </div>

        <div className="row">
          <div className="field">
            <label>Énergie</label>
            <select className="input" name="energie" value={vehicle.energie} onChange={onChange}>
              {energies.map(e => <option key={e} value={e}>{e}</option>)}
            </select>
          </div>

          <div className="field">
            <label>Boîte</label>
            <select className="input" name="boite_vitesses" value={vehicle.boite_vitesses} onChange={onChange}>
              {boites.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>
        </div>

        <div className="row">
          <div className="field">
            <label>Puissance fiscale (CV)</label>
            <input className="input" type="number" name="puissance_fiscale" value={vehicle.puissance_fiscale} onChange={onChange} min="1" />
          </div>

          <div className="field" style={{alignSelf:'flex-end'}}>
            <button className="btn" type="submit" disabled={loading}>{loading ? 'Calcul...' : 'Prédire'}</button>
          </div>
        </div>

        {error && <div style={{color:'#ffb4b4', marginTop:8}}>{error}</div>}
      </form>

      <div className="results">
        {result && <Results data={result} />}
      </div>
    </div>
  )
}