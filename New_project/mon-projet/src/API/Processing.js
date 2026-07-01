import request from "../Axios/axios"

function extractErrorMessage(error) {
  const detail = error?.response?.data?.detail
  if (!detail) return "Une erreur inattendue est survenue."
  if (Array.isArray(detail)) return detail.map((e) => e.msg ?? JSON.stringify(e)).join(", ")
  return String(detail)
}

export const uploadFiles = async ({ anciennete, fichier_vl_n, comptes_annuels, fichier_vl_n_1 = null }) => {
  const formData = new FormData()
  formData.append("anciennete", anciennete)
  formData.append("fichier_vl_n", fichier_vl_n)
  formData.append("comptes_annuels", comptes_annuels)
  if (fichier_vl_n_1) formData.append("fichier_vl_n_1", fichier_vl_n_1)
  try {
    const response = await request.post("/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const computeBilan = async (data) => {
  try {
    const response = await request.post("/bilan/", data)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const computeCapitauxPropres = async (data) => {
  try {
    const response = await request.post("/capitaux-propres/", data)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const computeCompteResultat = async (data) => {
  try {
    const response = await request.post("/compte-resultat/", data)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const computeExpositionPortefeuille = async (data) => {
  try {
    const response = await request.post("/exposition-portefeuille/", data)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const computeSommesDistribuables = async (data) => {
  try {
    const response = await request.post("/sommes-distribuables/", data)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const generatePdf = async ({ bilan, compte_resultat, capitaux_propres, exposition_portefeuille, sommes_distribuables, nom_fond, date_cloture }) => {
  try {
    const response = await request.post("/generatePdf/", {
      bilan,
      compte_resultat,
      capitaux_propres,
      exposition_portefeuille,
      sommes_distribuables,
      nom_fond,
      date_cloture,
    }, { responseType: "blob" })
    return response.data  // Blob PDF
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}