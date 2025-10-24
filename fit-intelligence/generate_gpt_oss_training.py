#!/usr/bin/env python3
"""
Generate high-quality training data for GPT-OSS FIT Intelligence
Focuses on accuracy, FIT IDs, and geographic precision
"""

import json
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
import chromadb

class GPTOSSTrainingGenerator:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.collection = self.client.get_collection("commercial_fit_sites")
        
        # Accurate UK postcode mappings
        self.city_postcodes = {
            "Aberdeen": ["AB10", "AB11", "AB12", "AB13", "AB14", "AB15", "AB16", "AB21", "AB22", "AB23", "AB24", "AB25", "AB30", "AB31", "AB32", "AB33", "AB34", "AB35", "AB36", "AB37", "AB38", "AB39", "AB41", "AB42", "AB43", "AB44", "AB45", "AB51", "AB52", "AB53", "AB54", "AB55", "AB56"],
            "Edinburgh": ["EH1", "EH2", "EH3", "EH4", "EH5", "EH6", "EH7", "EH8", "EH9", "EH10", "EH11", "EH12", "EH13", "EH14", "EH15", "EH16", "EH17", "EH18", "EH19", "EH20", "EH21", "EH22", "EH23", "EH24", "EH25", "EH26", "EH27", "EH28", "EH29", "EH30"],
            "Glasgow": ["G1", "G2", "G3", "G4", "G5", "G11", "G12", "G13", "G14", "G15", "G20", "G21", "G22", "G23", "G31", "G32", "G33", "G34", "G40", "G41", "G42", "G43", "G44", "G45", "G46", "G51", "G52", "G53", "G60", "G61", "G62", "G63", "G64", "G65", "G66", "G67", "G68", "G69", "G70", "G71", "G72", "G73", "G74", "G75", "G76", "G77", "G78", "G79", "G81", "G82", "G83", "G84"],
            "Yorkshire": ["YO1", "YO7", "YO8", "YO10", "YO11", "YO12", "YO13", "YO14", "YO15", "YO16", "YO17", "YO18", "YO19", "YO21", "YO22", "YO23", "YO24", "YO25", "YO26", "YO30", "YO31", "YO32", "YO41", "YO42", "YO43", "YO51", "YO60", "YO61", "YO62", "HU1", "HU2", "HU3", "HU4", "HU5", "HU6", "HU7", "HU8", "HU9", "HU10", "HU11", "HU12", "HU13", "HU14", "HU15", "HU16", "HU17", "HU18", "HU19", "HU20", "LS1", "LS2", "LS3", "LS4", "LS5", "LS6", "LS7", "LS8", "LS9", "LS10", "LS11", "LS12", "LS13", "LS14", "LS15", "LS16", "LS17", "LS18", "LS19", "LS20", "LS21", "LS22", "LS23", "LS24", "LS25", "LS26", "LS27", "LS28", "LS29", "BD1", "BD2", "BD3", "BD4", "BD5", "BD6", "BD7", "BD8", "BD9", "BD10", "BD11", "BD12", "BD13", "BD14", "BD15", "BD16", "BD17", "BD18", "BD19", "BD20", "BD21", "BD22", "BD23", "BD24", "HX1", "HX2", "HX3", "HX4", "HX5", "HX6", "HX7", "HD1", "HD2", "HD3", "HD4", "HD5", "HD6", "HD7", "HD8", "HD9", "WF1", "WF2", "WF3", "WF4", "WF5", "WF6", "WF7", "WF8", "WF9", "WF10", "WF11", "WF12", "WF13", "WF14", "WF15", "WF16", "WF17", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13", "S14", "S17", "S18", "S20", "S21", "S25", "S26", "S32", "S33", "S35", "S36", "S40", "S41", "S42", "S43", "S44", "S45", "S60", "S61", "S62", "S63", "S64", "S65", "S66", "S70", "S71", "S72", "S73", "S74", "S75", "S80", "S81", "DN1", "DN2", "DN3", "DN4", "DN5", "DN6", "DN7", "DN8", "DN9", "DN10", "DN11", "DN12", "DN14", "DN15", "DN16", "DN17", "DN18", "DN19", "DN20", "DN21", "DN22"],
            "London": ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E20", "EC1", "EC2", "EC3", "EC4", "N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10", "N11", "N12", "N13", "N14", "N15", "N16", "N17", "N18", "N19", "N20", "N21", "N22", "NW1", "NW2", "NW3", "NW4", "NW5", "NW6", "NW7", "NW8", "NW9", "NW10", "NW11", "SE1", "SE2", "SE3", "SE4", "SE5", "SE6", "SE7", "SE8", "SE9", "SE10", "SE11", "SE12", "SE13", "SE14", "SE15", "SE16", "SE17", "SE18", "SE19", "SE20", "SE21", "SE22", "SE23", "SE24", "SE25", "SE26", "SE27", "SE28", "SW1", "SW2", "SW3", "SW4", "SW5", "SW6", "SW7", "SW8", "SW9", "SW10", "SW11", "SW12", "SW13", "SW14", "SW15", "SW16", "SW17", "SW18", "SW19", "SW20", "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10", "W11", "W12", "W13", "W14", "WC1", "WC2"],
            "Manchester": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M11", "M12", "M13", "M14", "M15", "M16", "M17", "M18", "M19", "M20", "M21", "M22", "M23", "M24", "M25", "M26", "M27", "M28", "M29", "M30", "M31", "M32", "M33", "M34", "M35", "M38", "M40", "M41", "M43", "M44", "M45", "M46", "M50", "M60", "M61", "M90"],
            "Birmingham": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20", "B21", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30", "B31", "B32", "B33", "B34", "B35", "B36", "B37", "B38", "B40", "B42", "B43", "B44", "B45", "B46", "B47", "B48", "B49", "B50", "B60", "B61", "B62", "B63", "B64", "B65", "B66", "B67", "B68", "B69", "B70", "B71", "B72", "B73", "B74", "B75", "B76", "B77", "B78", "B79", "B80", "B90", "B91", "B92", "B93", "B94", "B95", "B96", "B97", "B98", "B99"],
            "Cardiff": ["CF1", "CF2", "CF3", "CF4", "CF5", "CF10", "CF11", "CF14", "CF15", "CF21", "CF22", "CF23", "CF24", "CF30", "CF31", "CF32", "CF33", "CF34", "CF35", "CF36", "CF37", "CF38", "CF39", "CF40", "CF41", "CF42", "CF43", "CF44", "CF45", "CF46", "CF47", "CF48", "CF61", "CF62", "CF63", "CF64", "CF71", "CF72", "CF81", "CF82", "CF83", "CF91", "CF95", "CF99"],
            "Bristol": ["BS1", "BS2", "BS3", "BS4", "BS5", "BS6", "BS7", "BS8", "BS9", "BS10", "BS11", "BS13", "BS14", "BS15", "BS16", "BS20", "BS21", "BS22", "BS23", "BS24", "BS25", "BS26", "BS27", "BS28", "BS29", "BS30", "BS31", "BS32", "BS34", "BS35", "BS36", "BS37", "BS39", "BS40", "BS41", "BS48", "BS49", "BS80", "BS98", "BS99"]
        }
        
        # Region mappings
        self.regions = {
            "Scotland": ["AB", "DD", "DG", "EH", "FK", "G", "HS", "IV", "KA", "KW", "KY", "ML", "PA", "PH", "TD", "ZE"],
            "Wales": ["CF", "LD", "LL", "NP", "SA", "SY"],
            "Northern England": ["BB", "BD", "BL", "CA", "DH", "DL", "DN", "FY", "HG", "HU", "HX", "LA", "LS", "NE", "OL", "PR", "S", "SR", "TS", "WF", "WN", "YO"],
            "Midlands": ["B", "CV", "DE", "DY", "LE", "NG", "NN", "ST", "WR", "WS", "WV"],
            "Southern England": ["BH", "BN", "BR", "BS", "CR", "CT", "DA", "EN", "GU", "HA", "HP", "KT", "ME", "MK", "OX", "PO", "RG", "RH", "RM", "SL", "SM", "SN", "SO", "SP", "TN", "TW", "UB"]
        }
        
        self.sample_sites = self.load_sample_sites()
    
    def load_sample_sites(self) -> Dict:
        """Load actual sites from database with FIT IDs"""
        sites_by_location = {}
        
        # Get all sites
        all_sites = self.collection.get(limit=40194, include=['metadatas'])
        
        for i, metadata in enumerate(all_sites['metadatas']):
            postcode = metadata.get('postcode', '')
            if postcode:
                # Assign a FIT ID based on index
                metadata['fit_id'] = 1000 + i
                
                # Group by postcode prefix
                prefix = postcode.split()[0] if ' ' in postcode else postcode[:3]
                if prefix not in sites_by_location:
                    sites_by_location[prefix] = []
                sites_by_location[prefix].append(metadata)
        
        return sites_by_location
    
    def get_sites_for_city(self, city: str, technology: str = None, min_capacity: int = None) -> List[Dict]:
        """Get actual sites for a specific city with filters"""
        valid_postcodes = self.city_postcodes.get(city, [])
        matching_sites = []
        
        for postcode in valid_postcodes:
            if postcode in self.sample_sites:
                for site in self.sample_sites[postcode]:
                    if technology and site.get('technology', '').lower() != technology.lower():
                        continue
                    if min_capacity and site.get('capacity_kw', 0) < min_capacity:
                        continue
                    matching_sites.append(site)
        
        return matching_sites[:10]  # Limit to 10 for training examples
    
    def generate_fit_id_query(self) -> Dict:
        """Generate FIT ID lookup training examples"""
        # Pick a random site
        all_postcodes = list(self.sample_sites.keys())
        if not all_postcodes:
            return None
        
        postcode = random.choice(all_postcodes)
        sites = self.sample_sites[postcode]
        if not sites:
            return None
        
        site = random.choice(sites)
        fit_id = site.get('fit_id', random.randint(1000, 40000))
        
        queries = [
            f"what is the rate for site {fit_id}",
            f"FIT ID {fit_id}",
            f"show me site {fit_id}",
            f"what's the capacity of installation {fit_id}",
            f"details for FIT {fit_id}"
        ]
        
        return {
            "instruction": random.choice(queries),
            "response": f"FIT ID {fit_id}:\\n• Technology: {site.get('technology', 'Unknown')}\\n• Capacity: {site.get('capacity_kw', 0):.0f}kW\\n• Location: {site.get('postcode', 'Unknown')}\\n• FIT Rate: {site.get('tariff_p_kwh', 0)}p/kWh\\n• Commissioned: {site.get('commission_date', 'Unknown')[:10] if site.get('commission_date') else 'Unknown'}"
        }
    
    def generate_geographic_query(self) -> Dict:
        """Generate geographically accurate queries"""
        city = random.choice(list(self.city_postcodes.keys()))
        technology = random.choice(['wind', 'solar', 'hydro'])
        min_capacity = random.choice([100, 250, 500, 1000])
        
        # Get actual matching sites
        sites = self.get_sites_for_city(city, technology, min_capacity)
        
        if not sites:
            response = f"No {technology} sites over {min_capacity}kW found near {city}"
        else:
            response = f"Found {len(sites)} {technology} sites over {min_capacity}kW near {city}:\\n\\n"
            for i, site in enumerate(sites[:5], 1):
                fit_id = site.get('fit_id', 1000 + i)
                response += f"{i}. FIT ID: {fit_id}\\n"
                response += f"   • Capacity: {site.get('capacity_kw', 0):.0f}kW\\n"
                response += f"   • Location: {site.get('postcode', 'Unknown')} ({city})\\n"
                response += f"   • FIT Rate: {site.get('tariff_p_kwh', 0)}p/kWh\\n\\n"
        
        queries = [
            f"{technology} sites over {min_capacity}kW near {city}",
            f"show me {technology} farms above {min_capacity}kW in {city}",
            f"what are the {technology} installations over {min_capacity}kW around {city}",
            f"list {technology} over {min_capacity} near {city}"
        ]
        
        return {
            "instruction": random.choice(queries),
            "response": response
        }
    
    def generate_conversation_chain(self) -> List[Dict]:
        """Generate multi-turn conversations with context"""
        city = random.choice(list(self.city_postcodes.keys()))
        technology = random.choice(['wind', 'solar'])
        sites = self.get_sites_for_city(city, technology, 250)
        
        if not sites:
            return []
        
        conversation = []
        
        # First query
        first_response = f"Found {len(sites)} {technology} sites over 250kW near {city}:\\n\\n"
        fit_ids = []
        for i, site in enumerate(sites[:3], 1):
            fit_id = site.get('fit_id', 1000 + i)
            fit_ids.append(fit_id)
            first_response += f"{i}. FIT ID: {fit_id}\\n"
            first_response += f"   • Capacity: {site.get('capacity_kw', 0):.0f}kW\\n"
            first_response += f"   • Location: {site.get('postcode', 'Unknown')}\\n\\n"
        
        conversation.append({
            "instruction": f"{technology} sites over 250kW near {city}",
            "response": first_response
        })
        
        # Follow-up: ask for FIT IDs
        conversation.append({
            "instruction": "what are their FIT IDs?",
            "context": first_response,
            "response": f"The FIT IDs for these sites are:\\n• " + "\\n• ".join(f"FIT ID {fid}" for fid in fit_ids)
        })
        
        # Follow-up: ask for rates
        rates_response = "The FIT rates for these sites are:\\n"
        for i, (fid, site) in enumerate(zip(fit_ids, sites[:3]), 1):
            rates_response += f"• FIT ID {fid}: {site.get('tariff_p_kwh', 0)}p/kWh\\n"
        
        conversation.append({
            "instruction": "what are their FIT rates?",
            "context": first_response,
            "response": rates_response
        })
        
        return conversation
    
    def generate_training_dataset(self, num_examples: int = 20000):
        """Generate complete training dataset"""
        training_data = []
        
        print("Generating GPT-OSS training data...")
        
        # 25% FIT ID queries
        for _ in range(num_examples // 4):
            example = self.generate_fit_id_query()
            if example:
                training_data.append(example)
        
        # 25% Geographic queries
        for _ in range(num_examples // 4):
            example = self.generate_geographic_query()
            if example:
                training_data.append(example)
        
        # 25% Conversation chains
        for _ in range(num_examples // 4 // 3):  # Each chain has 3 turns
            chain = self.generate_conversation_chain()
            training_data.extend(chain)
        
        # 25% Mixed queries
        for _ in range(num_examples // 4):
            if random.random() < 0.5:
                example = self.generate_fit_id_query()
            else:
                example = self.generate_geographic_query()
            if example:
                training_data.append(example)
        
        # Save in multiple formats
        
        # 1. JSONL format for fine-tuning
        with open('gpt_oss_training.jsonl', 'w') as f:
            for example in training_data:
                f.write(json.dumps(example) + '\\n')
        
        # 2. Conversation format
        with open('gpt_oss_conversations.json', 'w') as f:
            conversations = []
            for example in training_data:
                conv = {
                    "messages": [
                        {"role": "system", "content": "You are a FIT Intelligence assistant. Always include FIT IDs and ensure geographic accuracy."},
                        {"role": "user", "content": example['instruction']},
                        {"role": "assistant", "content": example['response']}
                    ]
                }
                if 'context' in example:
                    conv['messages'].insert(2, {"role": "assistant", "content": example['context']})
                conversations.append(conv)
            json.dump(conversations, f, indent=2)
        
        print(f"✅ Generated {len(training_data)} training examples")
        print(f"📁 Saved to gpt_oss_training.jsonl and gpt_oss_conversations.json")
        
        # Print statistics
        fit_id_queries = sum(1 for ex in training_data if 'FIT ID' in ex.get('instruction', ''))
        geographic_queries = sum(1 for ex in training_data if any(city in ex.get('instruction', '') for city in self.city_postcodes.keys()))
        context_queries = sum(1 for ex in training_data if 'context' in ex)
        
        print(f"\\n📊 Training Data Statistics:")
        print(f"  • FIT ID queries: {fit_id_queries}")
        print(f"  • Geographic queries: {geographic_queries}")
        print(f"  • Context-aware queries: {context_queries}")
        
        return training_data

if __name__ == "__main__":
    generator = GPTOSSTrainingGenerator()
    generator.generate_training_dataset(20000)
    
    print("\\n🎯 Next steps:")
    print("1. Fine-tune GPT-OSS: ollama create gpt-oss-fit -f Modelfile")
    print("2. Test the model: ollama run gpt-oss-fit")
    print("3. Evaluate accuracy on test queries")