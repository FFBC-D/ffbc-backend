from src.common.admin.use_cases.link_m2m_object import AdminLinkM2mObjectUseCase


class AdminLinkMeasureCategoryToProductCategory(AdminLinkM2mObjectUseCase):
    main_model_repository_attr_name = "product_category_admin"
    link_model_repository_attr_name = "measure_category_admin"
    link_model_field_name = "measure_categories"
