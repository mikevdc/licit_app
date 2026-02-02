# Documentación de API: Licit API (v0.1.0)

Documentación generada automáticamente basada en la especificación OpenAPI v3.1.0.
**Base URL:** `/api/v1`

## 📋 Resumen de Endpoints
**Leyenda:** 🔒 = Requiere Autenticación (Bearer Token)

### 🔐 Autenticación (Auth)
| Método | Ruta | Resumen | Descripción |
| :--- | :--- | :--- | :--- |
| **POST** | `/auth/login` | **Login** | Intercambia credenciales por token de acceso (OAuth2). |

### 👤 Usuarios (Users)
| Método | Ruta | Resumen | Descripción |
| :--- | :--- | :--- | :--- |
| **POST** | `/users/` | **Register User** | Registro de nuevos usuarios. |
| **GET** | `/users/me` | **Read User Me** | 🔒 Obtiene perfil del usuario actual. |
| **PATCH** | `/users/me` | **Update User Me** | 🔒 Actualiza datos del perfil propio. |
| **DELETE** | `/users/me` | **Delete User Me** | 🔒 Elimina la cuenta actual. |
| **POST** | `/users/me/password`| **Change Password** | 🔒 Cambia la contraseña actual. |

### 🔨 Subastas (Auctions)
| Método | Ruta | Resumen | Descripción |
| :--- | :--- | :--- | :--- |
| **GET** | `/auctions/` | **List Auctions** | Lista todas las subastas. |
| **POST** | `/auctions/` | **Create Auction** | 🔒 Crea una nueva subasta. |
| **GET** | `/auctions/{auction_id}` | **Get Auction** | Detalle de una subasta por ID. |
| **PATCH** | `/auctions/{auction_id}/details`| **Update Details** | 🔒 Modifica título/descripción. |
| **POST** | `/auctions/{auction_id}/cancel` | **Cancel Auction** | 🔒 Cancela una subasta activa. |

### 💰 Pujas (Bids)
| Método | Ruta | Resumen | Descripción |
| :--- | :--- | :--- | :--- |
| **POST** | `/bids/` | **Place Bid** | Realiza una puja. |
| **GET** | `/bids/auction/{auction_id}`| **List Auction Bids** | Historial de pujas de una subasta. |
| **DELETE** | `/bids/{bid_id}` | **Retract Bid** | Retira una puja (⚠️ *Ver nota técnica*). |

### 💓 System
| Método | Ruta | Resumen | Descripción |
| :--- | :--- | :--- | :--- |
| **GET** | `/health` | **Health Check** | Verificación de estado de la API. |

---

## 🚀 Propuesta de Nuevos Endpoints (Roadmap)
Para completar la funcionalidad del sistema de subastas, se sugiere implementar:

### 1. Gestión de Imágenes (Multimedia)
* `POST /auctions/{id}/images`: Subida de fotos del producto (multipart/form-data).
* `DELETE /auctions/{id}/images/{image_id}`: Eliminación de fotos.

### 2. Dashboard de Usuario
* `GET /users/me/auctions`: Listado de "Mis Ventas".
* `GET /users/me/bids`: Listado de "Mis Pujas" (historial y estado).

### 3. Búsqueda y Filtros
* `GET /auctions/search`: Búsqueda avanzada con query params (`?q=laptop&min_price=100`).

### 4. Perfil Público y Reputación
* `GET /users/{user_id}/profile`: Información pública del vendedor.
* `POST /users/{user_id}/reviews`: Sistema de reseñas post-venta.

### 5. Recuperación de Cuenta
* `POST /auth/forgot-password`: Solicitud de reset de contraseña.
* `POST /auth/reset-password`: Ejecución del cambio de contraseña.

### 6. Administración
* `DELETE /admin/auctions/{id}`: Moderación de contenido.
* `PUT /admin/users/{id}/ban`: Bloqueo de usuarios.

---

## ⚠️ Notas Técnicas

### Incidencia en `DELETE /api/v1/bids/{bid_id}`
El diseño actual requiere un `requestBody` con el esquema `User` para borrar una puja.
* **Riesgo:** Muchos proxies y clientes HTTP eliminan el cuerpo en peticiones DELETE.
* **Solución:** Eliminar el body y validar la propiedad de la puja mediante el token `Authorization` del header.