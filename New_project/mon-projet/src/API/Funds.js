import request from "../Axios/axios"

function extractErrorMessage(error) {
  const detail = error?.response?.data?.detail
  if (!detail) return "Une erreur inattendue est survenue."
  if (Array.isArray(detail)) return detail.map((e) => e.msg ?? JSON.stringify(e)).join(", ")
  return String(detail)
}

export const getFunds = async (page = 1, pageSize = 10, search = "") => {
  try {
    const response = await request.get("/funds/", {
      params: {
        page,
        page_size: pageSize,
        ...(search ? { search } : {}),
      },
    })
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

// La route est POST /companies/{company_id}/funds/
export const CreateFund = async (companyId, data) => {
  try {
    const response = await request.post(`/companies/${companyId}/funds/`, data)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const UpdateFund = async (id, companyId, data) => {
  try {
    const response = await request.patch(`/funds/${id}`, data, {
      params: { company_id: companyId },
    })
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

export const DeleteFund = async (id) => {
  try {
    const response = await request.delete(`/funds/${id}`)
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}

// Fonds d'une société spécifique
export const getFundsByCompany = async (companyId, page = 1, pageSize = 10) => {
  try {
    const response = await request.get(`/companies/${companyId}/funds/`, {
      params: { page, page_size: pageSize },
    })
    return response.data
  } catch (error) {
    throw new Error(extractErrorMessage(error))
  }
}