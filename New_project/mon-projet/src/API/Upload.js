import request from "../Axios/axios"

function extractErrorMessage(error) {
  const detail = error?.response?.data?.detail
  if (!detail) return "Une erreur inattendue est survenue."
  if (Array.isArray(detail)) return detail.map((e) => e.msg ?? JSON.stringify(e)).join(", ")
  return String(detail)
}

/**
 * Upload des fichiers pour générer les comptes annuels.
 * @param {string} anciennete - "A" ou "N"
 * @param {File} fichier_vl_n - fichier VL N (obligatoire)
 * @param {File} comptes_annuels - PDF comptes annuels (obligatoire)
 * @param {File|null} fichier_vl_n_1 - fichier VL N-1 (obligatoire si anciennete === "A")
 */
export const uploadFiles = async ({ anciennete, fichier_vl_n, comptes_annuels, fichier_vl_n_1 = null }) => {
  const formData = new FormData()
  formData.append("anciennete", anciennete)
  formData.append("fichier_vl_n", fichier_vl_n)
  formData.append("comptes_annuels", comptes_annuels)
  if (fichier_vl_n_1) {
    formData.append("fichier_vl_n_1", fichier_vl_n_1)
  }

  try {
    const response = await request.post("/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}