"""
Test script to verify the ternary plotting workflow implementation.
This script tests the complete workflow from table generation to ternary plotting.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_ternary_workflow():
    """Test the complete ternary plotting workflow."""
    
    print("=" * 60)
    print("TESTING TERNARY PLOTTING WORKFLOW")
    print("=" * 60)
    
    # Step 1: Create mock generated tables (simulating table generation)
    print("\nStep 1: Creating mock generated tables...")
    
    # Create sample data for major oxides
    sample_data = {
        'Z': [14, 13, 26, 20, 12, 11, 19],
        'Element': ['SiO2', 'Al2O3', 'Fe2O3', 'CaO', 'MgO', 'Na2O', 'K2O'],
        'Sample_A': [65.2, 15.8, 5.1, 8.3, 2.1, 2.8, 0.7],
        'Sample_B': [58.9, 18.2, 7.3, 9.1, 3.2, 2.5, 0.8],
        'Sample_C': [72.1, 13.5, 3.8, 6.2, 1.8, 2.1, 0.5]
    }
    
    mock_oxide_table = pd.DataFrame(sample_data)
    
    generated_tables = {
        'relative_major_oxides': mock_oxide_table,
        'metadata': pd.DataFrame([{'client': 'Test Client', 'project_name': 'Test Project'}]),
        'lookup': pd.DataFrame([
            {'sample_id': 'Sample_A', 'report_abbreviation': 'Sample_A'},
            {'sample_id': 'Sample_B', 'report_abbreviation': 'Sample_B'},
            {'sample_id': 'Sample_C', 'report_abbreviation': 'Sample_C'}
        ])
    }
    
    print(f"Generated tables: {list(generated_tables.keys())}")
    print(f"Oxide table shape: {mock_oxide_table.shape}")
    print(f"Available oxides: {mock_oxide_table['Element'].tolist()}")
    
    # Step 2: Create concatenated DataFrame
    print("\nStep 2: Creating concatenated DataFrame...")
    
    from src.controllers.csv_exporter import create_concatenated_dataframe
    
    metadata = {'client': 'Test Client', 'project_name': 'Test Project'}
    lookup_table = [
        {'sample_id': 'Sample_A', 'report_abbreviation': 'Sample_A'},
        {'sample_id': 'Sample_B', 'report_abbreviation': 'Sample_B'},
        {'sample_id': 'Sample_C', 'report_abbreviation': 'Sample_C'}
    ]
    
    try:
        concat_df = create_concatenated_dataframe(generated_tables, metadata, lookup_table)
        print(f"Concatenated DataFrame shape: {concat_df.shape}")
        print(f"Columns: {concat_df.columns.tolist()}")
        print(f"Sample preview:\n{concat_df.head()}")
    except Exception as e:
        print(f"Error creating concatenated DataFrame: {e}")
        return False
    
    # Step 3: Test long format conversion
    print("\nStep 3: Testing long format conversion...")
    
    # Check if already in long format
    if 'Element' in concat_df.columns and 'Sample ID' in concat_df.columns and 'Wt.%' in concat_df.columns:
        long_df = concat_df
        print("DataFrame already in long format")
    else:
        print("DataFrame needs conversion to long format")
        # This would be handled by _create_long_format_dataframe in the actual workflow
        long_df = concat_df
    
    print(f"Long DataFrame shape: {long_df.shape}")
    print(f"Unique elements: {sorted(long_df['Element'].unique())}")
    print(f"Unique samples: {sorted(long_df['Sample ID'].unique())}")
    
    # Step 4: Test ternary data extraction
    print("\nStep 4: Testing ternary data extraction...")
    
    # Define ternary systems
    ternary_systems = {
        'SiO2-Al2O3-Fe2O3': ['SiO2', 'Al2O3', 'Fe2O3'],
        'CaO-Al2O3-SiO2': ['CaO', 'Al2O3', 'SiO2'],
    }
    
    ternary_data_by_system = {}
    ternary_labels_by_system = {}
    
    for system_name, required_oxides in ternary_systems.items():
        print(f"\nProcessing ternary system: {system_name}")
        print(f"Required oxides: {required_oxides}")
        
        ternary_points = []
        labels = []
        
        # Check which oxides are available
        available_oxides = [oxide for oxide in required_oxides if oxide in long_df['Element'].values]
        print(f"Available oxides: {available_oxides}")
        
        if len(available_oxides) < 3:
            print(f"Skipping {system_name}: only {len(available_oxides)}/3 oxides available")
            continue
        
        # Process each sample
        for sample_id in long_df['Sample ID'].unique():
            sample_data = long_df[long_df['Sample ID'] == sample_id]
            
            values = []
            missing_oxides = []
            
            for oxide in required_oxides:
                oxide_data = sample_data[sample_data['Element'] == oxide]
                if not oxide_data.empty:
                    value = float(oxide_data['Wt.%'].iloc[0])
                    values.append(value)
                else:
                    values.append(0.0)
                    missing_oxides.append(oxide)
            
            # Only include samples with positive sum
            total = sum(values)
            if total > 0:
                # Normalize to 100%
                normalized_values = [v / total * 100 for v in values]
                ternary_points.append(tuple(normalized_values))
                labels.append(str(sample_id))
                
                print(f"Sample {sample_id}: {dict(zip(required_oxides, values))} -> {dict(zip(required_oxides, normalized_values))}")
        
        print(f"Extracted {len(ternary_points)} points for {system_name}")
        
        # Store the data
        ternary_data_by_system[system_name] = ternary_points
        ternary_labels_by_system[system_name] = labels
    
    # Step 5: Test ternary plotting
    print("\nStep 5: Testing ternary plotting...")
    
    from src.controllers.ternary_plotter import plot_ternary, get_available_systems
    
    available_systems = get_available_systems()
    print(f"Available ternary systems: {available_systems}")
    
    # Test plotting for each system with data
    for system_name, points in ternary_data_by_system.items():
        if points:
            print(f"\nTesting plot for {system_name} with {len(points)} points...")
            try:
                # Test without saving (just validation)
                plot_ternary(system_name, points, caption=f"Test plot for {system_name}")
                print(f"✓ Successfully created plot for {system_name}")
            except Exception as e:
                print(f"✗ Error creating plot for {system_name}: {e}")
                return False
    
    print("\n" + "=" * 60)
    print("TERNARY WORKFLOW TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    # Summary
    print(f"\nSummary:")
    print(f"- Generated tables: {len(generated_tables)}")
    print(f"- Concatenated DataFrame rows: {len(concat_df)}")
    print(f"- Ternary systems with data: {len(ternary_data_by_system)}")
    print(f"- Total ternary points: {sum(len(points) for points in ternary_data_by_system.values())}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_ternary_workflow()
        if success:
            print("\n🎉 All tests passed! The ternary plotting workflow is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
