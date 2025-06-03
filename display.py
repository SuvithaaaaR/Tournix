from __init__ import db, app
from sqlalchemy import inspect
from tabulate import tabulate  # Add tabulate for table formatting

def display_table_structure():
    """Display the structure of all tables in the database"""
    inspector = inspect(db.engine)
    
    print("=" * 80)
    print("DATABASE STRUCTURE".center(80))
    print("=" * 80)
    
    # Get all table names
    tables = inspector.get_table_names()
    
    for table_name in tables:
        print("\n" + "-" * 80)
        print(f"TABLE: {table_name}")
        print("-" * 80)
        
        # Get column information
        columns = inspector.get_columns(table_name)
        column_data = []
        for column in columns:
            nullable = "NULL" if column['nullable'] else "NOT NULL"
            primary_key = "PRIMARY KEY" if column.get('primary_key', False) else ""
            column_data.append([column['name'], str(column['type']), nullable, primary_key])
        
        print("\nColumns:")
        print(tabulate(column_data, headers=["Name", "Type", "Nullable", "Key"], tablefmt="grid"))
        
        # Add data display section
        try:
            # Execute a query to get all data from the table
            result = db.session.execute(db.text(f"SELECT * FROM {table_name} LIMIT 10"))
            columns = result.keys()
            rows = result.fetchall()
            
            if rows:
                print("\nTable Data (up to 10 rows):")
                print(tabulate(rows, headers=columns, tablefmt="grid"))
                
                # Show row count
                count_result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table_name}"))
                total_rows = count_result.scalar()
                print(f"Total rows: {total_rows}")
            else:
                print("\nTable Data: No data available")
        except Exception as e:
            print(f"\nError retrieving data: {e}")
        
        # Get foreign key information
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            fk_data = []
            for fk in foreign_keys:
                fk_data.append([
                    ', '.join(fk['constrained_columns']), 
                    fk['referred_table'], 
                    ', '.join(fk['referred_columns'])
                ])
            
            print("\nForeign Keys:")
            print(tabulate(fk_data, headers=["Column", "Referenced Table", "Referenced Column"], tablefmt="grid"))
        
        # Get index information
        indices = inspector.get_indexes(table_name)
        if indices:
            index_data = []
            for index in indices:
                unique = "UNIQUE" if index['unique'] else "STANDARD"
                index_data.append([index['name'], unique, ', '.join(index['column_names'])])
            
            print("\nIndices:")
            print(tabulate(index_data, headers=["Name", "Type", "Columns"], tablefmt="grid"))

def display_model_relationships():
    """Display the ORM model relationships"""
    # Import here to avoid circular imports
    from models import User, Venue, Tournament, Team, Player, Match, MatchResult
    
    print("\n" + "=" * 80)
    print("MODEL RELATIONSHIPS".center(80))
    print("=" * 80)
    
    models = [User, Venue, Tournament, Team, Player, Match, MatchResult]
    
    for model in models:
        print(f"\n{model.__name__}:")
        relationship_data = []
        for relationship in inspect(model).relationships:
            direction = "many-to-one" if relationship.direction.name == "MANYTOONE" else \
                       "one-to-many" if relationship.direction.name == "ONETOMANY" else \
                       "many-to-many" if relationship.direction.name == "MANYTOMANY" else "one-to-one"
            relationship_data.append([relationship.key, direction, relationship.target.name])
        
        print(tabulate(relationship_data, headers=["Attribute", "Type", "Related Model"], tablefmt="grid"))

def display_database_summary():
    """Display a summary of the database"""
    print("\n" + "=" * 80)
    print("DATABASE SUMMARY".center(80))
    print("=" * 80)
    
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    table_stats = []
    for table_name in tables:
        columns = inspector.get_columns(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indices = inspector.get_indexes(table_name)
        table_stats.append([
            table_name, 
            len(columns), 
            len(foreign_keys), 
            len(indices)
        ])
    
    print("\nTables Summary:")
    print(tabulate(table_stats, headers=["Table Name", "Columns", "Foreign Keys", "Indices"], tablefmt="grid"))
    print(f"\nTotal tables: {len(tables)}")

if __name__ == "__main__":
    # Create application context before accessing db
    with app.app_context():
        display_table_structure()
        display_model_relationships()
        display_database_summary()
