package edu.northwestern.cbits.purple.rapidminer;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.Iterator;

import com.rapidminer.operator.learner.tree.Edge;
import com.rapidminer.operator.learner.tree.SplitCondition;
import com.rapidminer.operator.learner.tree.Tree;
import com.rapidminer.operator.learner.tree.TreeModel;
import com.rapidminer.operator.tools.BodySerializer;
import com.rapidminer.operator.tools.IOObjectSerializer;
import com.rapidminer.operator.tools.SerializationType;

public class BinaryOutputReader 
{
	private static String hexToOperator(char value)
	{
		String hex = String.format("%h", value);
		
		if ("2264".equalsIgnoreCase(hex))
			return "<=";
		else if ("3e".equalsIgnoreCase(hex))
			return ">";

		System.out.format("UNKNOWN: %s", hex);

		return "" + value;
	}
	
	private static String printNode(Tree node, int indent)
	{
		StringBuffer sb = new StringBuffer();

		sb.append(System.getProperty("line.separator"));
		
		for (int i = 0; i < indent; i++)
			sb.append(" ");
		
		if (node.isLeaf())
			sb.append("return '" + node.getLabel() + "';" + System.getProperty("line.separator"));
		else
		{
			Iterator<Edge> edges = node.childIterator();
			
			boolean first = true;
			
			while (edges.hasNext())
			{
				Edge e = edges.next();
				
				SplitCondition split = e.getCondition();
				
				String op = BinaryOutputReader.hexToOperator(split.getRelation().charAt(0));
				
				if (first)
					sb.append("if (example['" + split.getAttributeName() + "'] " + op + " " + split.getValueString() + ") {");
				else
				{
					for (int i = 0; i < indent; i++)
						sb.append(" ");

					sb.append("else if (example['" + split.getAttributeName() + "'] " + op + " " + split.getValueString() + ") {");
				}
				
				sb.append(BinaryOutputReader.printNode(e.getChild(), indent + 1));
				
				for (int i = 0; i < indent; i++)
					sb.append(" ");
				
				sb.append("}" + System.getProperty("line.separator"));
				
				first = false;
			}
		}
		
		return sb.toString();
	}
	
	public static void main(String[] args) 
	{
		try 
		{
			IOObjectSerializer serializer = IOObjectSerializer.getInstance();
			
			InputStream in = new FileInputStream(new File("C:/Users/cjkarr/Downloads/c45-0-3"));
			
			Object o = serializer.deserialize(in);
			
			System.out.println("// " + o.getClass());

			if (o instanceof TreeModel)
			{
				TreeModel treeModel = (TreeModel) o;
				
				Tree root = treeModel.getRoot();
				
				System.out.println(BinaryOutputReader.printNode(root, 0));
			}
		} 
		catch (FileNotFoundException e) 
		{
			e.printStackTrace();
		} 
		catch (IOException e) 
		{
			e.printStackTrace();
		}
	}
}
