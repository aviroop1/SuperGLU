package Ontology;
/**
 * OntologyConverter  Class
 * @author tirthmehta
 */

import Core.BaseMessage;
import Core.Message;
import Core.VHMessage;
import Ontology.Mappings.FieldData;
import Ontology.Mappings.FieldMap;
import Ontology.Mappings.MessageMap;
import Ontology.Mappings.MessageTemplate;
import Ontology.Mappings.MessageTwoWayMap;
import Ontology.Mappings.MessageType;
import Ontology.Mappings.NestedAtomic;
import Util.SerializationConvenience;
import Util.StorageToken;
import java.util.*;


public class OntologyConverter {
	static MessageMap correctMap;
	
	private List<MessageMap> messageMaps;
	
	public OntologyConverter()
	{
		messageMaps=null;
	}
	// Test code makes a mapping for scenarioName; Mapping is variable testMap; x = [testMap,]
	public OntologyConverter(List<MessageMap> x)
	{
		messageMaps=x;
	}
	

	public boolean isValidSourceMsg(BaseMessage b,StorageToken input,String firstwordkey)
	{
		//CURRENTLY SINCE THERE IS ONLY 1 MESSAGEMAP IN THE LIST OF MESSAGEMAPS
				for(MessageMap x:messageMaps)
				{
					int count=0;
					MessageType in=x.getInMsgType();
					MessageType out=x.getOutMsgType();
					StorageToken ST_inMsgType=in.saveToToken();
					StorageToken ST_outMsgType=out.saveToToken();
				
					
					if(input.getClassId().equals(ST_inMsgType.getItem(in.MESSAGE_TYPE_CLASS_ID_KEY)))
					{
						count=1;
					}
					MessageTemplate mTemp= in.getMessageTemplate();
					ArrayList<FieldData> arr=mTemp.getDefaultFieldData();
					for(FieldData y:arr)
					{
						if(y.getFieldData().equals(firstwordkey))
							{
								count+=1;
								correctMap=x;
								break;
							}			
					}
					if(count==2)
						return true;
					
				}
				return false;
	}
	
	public BaseMessage convert(BaseMessage b,StorageToken input)
	{
		MessageType out=correctMap.getOutMsgType();
		MessageTemplate mtemp=out.getMessageTemplate();
		StorageToken target=mtemp.createTargetStorageToken(out.getClassId());
		
				
		ArrayList<FieldMap> mappingList=correctMap.getFieldMappings();
		for(FieldMap maps: mappingList)
		{
			
			
			NestedAtomic inFields=maps.getInFields();
			String inFieldsIndex=inFields.getIndex();
			NestedAtomic outFields=maps.getOutFields();
			String outFieldsIndex=outFields.getIndex();
			
			if(outFieldsIndex.equals("verb"))
			{
				target.setItem(Message.VERB_KEY,input.getItem(VHMessage.FIRST_WORD_KEY));
			}
			else if(outFieldsIndex.equals("object"))
			{
				target.setItem(Message.OBJECT_KEY, input.getItem(VHMessage.BODY_KEY));
			}
			
			
		
		}
		BaseMessage targetObj=(BaseMessage) SerializationConvenience.untokenizeObject(target);
		
		if(targetObj!=null)
			return targetObj;
		else
			return null;
		
	}

}
