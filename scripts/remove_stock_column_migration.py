#!/usr/bin/env python3
"""
Database migration script to remove estimated_stock_status column from motors table
Since the cigarette machine doesn't track actual stock quantities, this information is not meaningful.

Usage: python3 remove_stock_column_migration.py [database_path]
"""

import sqlite3
import os
import sys
from datetime import datetime

def backup_database(db_path):
    """Create backup of database before migration"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        # Copy database file
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup creato: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Errore nel backup: {e}")
        return None

def check_column_exists(cursor, table_name, column_name):
    """Check if column exists in table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

def migrate_database(db_path):
    """Remove estimated_stock_status column from motors table"""
    print(f"🔄 Migrazione database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column exists
        if not check_column_exists(cursor, 'motors', 'estimated_stock_status'):
            print("✅ La colonna 'estimated_stock_status' non esiste già. Nessuna migrazione necessaria.")
            return True

        print("📋 Colonna 'estimated_stock_status' trovata. Rimozione in corso...")

        # Get current table structure
        cursor.execute("PRAGMA table_info(motors)")
        table_info = cursor.fetchall()

        # Build new column list without estimated_stock_status
        new_columns = []
        for column in table_info:
            column_name = column[1]
            if column_name != 'estimated_stock_status':
                column_type = column[2]
                not_null = 'NOT NULL' if column[3] else ''
                default_value = f"DEFAULT {column[4]}" if column[4] is not None else ''
                primary_key = 'PRIMARY KEY' if column[5] else ''

                column_def = f"{column_name} {column_type} {not_null} {default_value} {primary_key}".strip()
                new_columns.append(column_def)

        # Create new table without stock column
        create_table_sql = f"""
        CREATE TABLE motors_new (
            {', '.join(new_columns)}
        )
        """

        cursor.execute(create_table_sql)
        print("📋 Nuova tabella 'motors_new' creata")

        # Copy data (excluding stock status column)
        data_columns = [col.split()[0] for col in new_columns]  # Get column names only
        columns_str = ', '.join(data_columns)

        cursor.execute(f"INSERT INTO motors_new ({columns_str}) SELECT {columns_str} FROM motors")
        print(f"📋 Dati copiati nella nuova tabella ({cursor.rowcount} righe)")

        # Drop old table and rename new one
        cursor.execute("DROP TABLE motors")
        cursor.execute("ALTER TABLE motors_new RENAME TO motors")

        conn.commit()
        print("✅ Migrazione completata con successo!")

        return True

    except Exception as e:
        print(f"❌ Errore durante migrazione: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def main():
    """Main migration function"""
    # Default database path
    default_db_path = "backend/sales_data.db"

    # Get database path from command line or use default
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = default_db_path

    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database non trovato: {db_path}")
        print(f"💡 Uso: python3 {sys.argv[0]} [percorso_database]")
        sys.exit(1)

    print(f"📊 Migrazione database distributore sigarette")
    print(f"🎯 Database: {db_path}")
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Create backup
    backup_path = backup_database(db_path)
    if not backup_path:
        print("❌ Impossibile creare backup. Migrazione annullata.")
        sys.exit(1)

    # Perform migration
    success = migrate_database(db_path)

    if success:
        print()
        print("🎉 MIGRAZIONE COMPLETATA!")
        print("✅ La colonna 'estimated_stock_status' è stata rimossa dalla tabella 'motors'")
        print(f"💾 Backup disponibile in: {backup_path}")
        print()
        print("📝 Modifiche applicate:")
        print("   - Rimossa colonna estimated_stock_status dalla tabella motors")
        print("   - Il sistema ora si focalizza solo su vendite e ricavi")
        print("   - Nessuna stima di stock (il distributore non traccia le quantità)")
    else:
        print()
        print("❌ MIGRAZIONE FALLITA!")
        print(f"💾 Database originale è ancora disponibile in: {backup_path}")

if __name__ == "__main__":
    main()