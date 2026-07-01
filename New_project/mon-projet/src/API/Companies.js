import request from "../Axios/axios"

function extractErrorMessage(error) {
  const detail = error?.response?.data?.detail
  if (!detail) return "Une erreur inattendue est survenue."
  if (Array.isArray(detail)) return detail.map((e) => e.msg ?? JSON.stringify(e)).join(", ")
  return String(detail)
}
 
export const getCompanies = async (page = 1, pageSize = 10, search) => {
  try {
    const response = await request.get("/companies", {
      params: { page, page_size: pageSize, search },
    })
    return response.data
    // Retourne l'objet complet :
    // { items, page, page_size, total_items, total_pages, next_page, previous_page }
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const CreateCompany = async (data) => {
  try {
    const response = await request.post("/companies", data)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const UpdateCompany = async (id, data) => {
  try {
    const response = await request.patch(`/companies/${id}`, data)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const DeleteCompany = async (id) => {
  try {
    const response = await request.delete(`/companies/${id}`)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}