import asyncio
from RAG import RAGManager


async def main():
    print("Инициализация RAG Manager...")
    rag = RAGManager()
    await rag.initialize()
    
    try:
        print("\n=== Получение списка документов ===")
        documents = await rag.get_documents()
        print(f"Найдено документов: {len(documents)}")
        
        for doc in documents:
            print(f"\nID: {doc['id']}")
            print(f"Имя файла: {doc['filename']}")
            print(f"Размер: {doc['file_size']} байт")
            print(f"Фрагментов: {doc['chunk_count']}")
        
        if documents:
            document_id = documents[0]['id']
            
            print(f"\n=== Поиск в документе {document_id} ===")
            query = "Расскажи о основных темах в документе"
            
            print(f"Запрос: {query}")
            
            result = await rag.generate_answer(
                query=query,
                document_id=document_id
            )
            
            print(f"\nОтвет:\n{result['answer']}")
            
            print("\nИсточники:")
            for source in result['sources']:
                print(f"  - {source['filename']} (релевантность: {source['similarity']:.2%})")
        
        else:
            print("\nНет документов для демонстрации. Загрузите документы через веб-интерфейс.")
            
    finally:
        await rag.close()
        print("\nРабота завершена.")


if __name__ == "__main__":
    asyncio.run(main())

