"""
Initial migration - создание всех таблиц

Revision ID: 001
Revises: 
Create Date: 2026-03-29 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === COUNTRIES ===
    op.create_table(
        'countries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code'),
    )
    op.create_index(op.f('ix_countries_code'), 'countries', ['code'])

    # === REGIONS ===
    op.create_table(
        'regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_regions_country_id'), 'regions', ['country_id'])

    # === CITIES ===
    op.create_table(
        'cities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_cities_region_id'), 'cities', ['region_id'])

    # === LEGAL_FORMS ===
    op.create_table(
        'legal_forms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code'),
    )

    # === PRODUCT_NAMES ===
    op.create_table(
        'product_names',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index(op.f('ix_product_names_name'), 'product_names', ['name'])

    # === USERS ===
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('first_name', sa.String(255), nullable=True),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('is_buyer', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('is_seller', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id'),
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'])

    # === SELLER_PROFILES ===
    op.create_table(
        'seller_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='none'),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('legal_form_id', sa.Integer(), nullable=True),
        sa.Column('owner_name', sa.String(255), nullable=True),
        sa.Column('owner_phone', sa.String(20), nullable=True),
        sa.Column('inn_unp', sa.String(20), nullable=True),
        sa.Column('passport_file', sa.String(512), nullable=True),
        sa.Column('registration_cert_file', sa.String(512), nullable=True),
        sa.Column('moderator_comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['legal_form_id'], ['legal_forms.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index(op.f('ix_seller_profiles_user_id'), 'seller_profiles', ['user_id'])
    op.create_index(op.f('ix_seller_profiles_inn_unp'), 'seller_profiles', ['inn_unp'])

    # === SHOWCASES ===
    op.create_table(
        'showcases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_profile_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_file', sa.String(512), nullable=True),
        sa.Column('country_id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=True),
        sa.Column('is_wholesale', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('is_retail', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('is_delivery_available', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('pickup_address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['seller_profile_id'], ['seller_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id']),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id']),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_showcases_seller_profile_id'), 'showcases', ['seller_profile_id'])

    # === PRODUCTS ===
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('showcase_id', sa.Integer(), nullable=False),
        sa.Column('product_name_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_per_kg', sa.Float(), nullable=False),
        sa.Column('quantity_in_stock', sa.Float(), nullable=False),
        sa.Column('image_file', sa.String(512), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('is_wholesale', sa.Boolean(), nullable=False, server_default='f'),
        sa.Column('is_retail', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('moderator_comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['showcase_id'], ['showcases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_name_id'], ['product_names.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_products_showcase_id'), 'products', ['showcase_id'])

    # === SUBSCRIPTIONS ===
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_profile_id', sa.Integer(), nullable=False),
        sa.Column('plan', sa.String(20), nullable=False, server_default='free'),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='t'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['seller_profile_id'], ['seller_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_subscriptions_seller_profile_id'), 'subscriptions', ['seller_profile_id'])

    # === PAYMENTS ===
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_profile_id', sa.Integer(), nullable=False),
        sa.Column('payment_type', sa.String(20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('requisites', sa.Text(), nullable=True),
        sa.Column('receipt_file', sa.String(512), nullable=True),
        sa.Column('receipt_uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('moderator_comment', sa.Text(), nullable=True),
        sa.Column('subscription_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['seller_profile_id'], ['seller_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_payments_seller_profile_id'), 'payments', ['seller_profile_id'])


def downgrade() -> None:
    # Удаляем таблицы в обратном порядке (из-за FK)
    op.drop_table('payments')
    op.drop_table('subscriptions')
    op.drop_table('products')
    op.drop_table('showcases')
    op.drop_table('seller_profiles')
    op.drop_table('users')
    op.drop_table('product_names')
    op.drop_table('legal_forms')
    op.drop_table('cities')
    op.drop_table('regions')
    op.drop_table('countries')